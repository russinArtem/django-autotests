from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Обновлённый комментарий'}
BAD_WORDS_DATA = [{'text': bad_word} for bad_word in BAD_WORDS]


def test_anonymous_user_cant_create_comment(
    client, detail_url, login_redirect_detail
):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, login_redirect_detail)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, news, detail_url, url_to_comments
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('data', BAD_WORDS_DATA)
def test_user_cant_use_bad_words(author_client, detail_url, data):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    response = author_client.post(detail_url, data=data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_non_author_cant_delete_comment(reader_client, comment, delete_url):
    assert reader_client.post(delete_url).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_after = Comment.objects.get()
    assert comment.text == comment_after.text
    assert comment.news == comment_after.news
    assert comment.author == comment_after.author


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_url,
    url_to_comments
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    assertRedirects(
        author_client.post(edit_url, data=FORM_DATA),
        url_to_comments
    )
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author


def test_non_author_cant_edit_comment(reader_client, comment, edit_url):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    assert reader_client.post(
        edit_url, data=FORM_DATA
    ).status_code == HTTPStatus.NOT_FOUND
    comment_after = Comment.objects.get(id=comment.id)
    assert comment_after.text == comment.text
    assert comment_after.news == comment.news
    assert comment_after.author == comment.author
