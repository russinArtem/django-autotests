from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from .conftest import COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

NEW_COMMENT_TEXT = 'Обновлённый комментарий'

FORM_DATA = {
    'comment_text': {'text': COMMENT_TEXT},
    'new_comment_text': {'text': NEW_COMMENT_TEXT}
}


def test_anonymous_user_cant_create_comment(client, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(detail_url, data=FORM_DATA['comment_text'])
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, news, detail_url, url_to_comments
):
    """Авторизованный пользователь может отправить комментарий."""
    assertRedirects(
        author_client.post(detail_url, data=FORM_DATA['comment_text']),
        url_to_comments
    )
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    assertFormError(
        author_client.post(
            detail_url, data={'text': BAD_WORDS[0]}
        ).context['form'],
        'text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_non_author_cant_delete_comment(
    reader_client, author, news, delete_url
):
    assert Comment.objects.count() == 1
    assert reader_client.post(delete_url).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_author_can_edit_comment(
    author,
    author_client,
    news,
    comment,
    edit_url,
    url_to_comments
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    assertRedirects(
        author_client.post(edit_url, data=FORM_DATA['new_comment_text']),
        url_to_comments
    )
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_non_author_cant_edit_comment(
    author, reader_client, news, comment, edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    assert reader_client.post(
        edit_url, data=FORM_DATA['new_comment_text']
    ).status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author
