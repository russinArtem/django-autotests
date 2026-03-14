from http import HTTPStatus
import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, id_news_for_args, detail_url, form_data
):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(reverse(detail_url, args=id_news_for_args), data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, author, news, id_news_for_args, detail_url, form_data
):
    """Авторизованный пользователь может отправить комментарий."""
    assertRedirects(
        author_client.post(
            reverse(detail_url, args=id_news_for_args),
            data=form_data
        ),
        f'{reverse(detail_url, args=id_news_for_args)}#comments'
    )
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(
    author_client, id_news_for_args, detail_url, bad_words_data
):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    assertFormError(
        author_client.post(
            reverse(detail_url, args=id_news_for_args), data=bad_words_data
        ).context['form'],
        list(bad_words_data.keys())[0],
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client,
    id_news_for_args,
    id_comment_for_args,
    detail_url,
    delete_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    assert Comment.objects.count() == 1
    response = author_client.post(
        reverse(delete_url, args=id_comment_for_args)
    )
    assertRedirects(
        response,
        f'{reverse(detail_url, args=id_news_for_args)}#comments'
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    reader_client, delete_url, id_comment_for_args
):
    assert Comment.objects.count() == 1
    assert reader_client.post(
        reverse(delete_url, args=id_comment_for_args)
    ).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client,
    comment,
    id_news_for_args,
    id_comment_for_args,
    detail_url,
    edit_url,
    new_form_data
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    assertRedirects(
        author_client.post(
            reverse(edit_url, args=id_comment_for_args), data=new_form_data
        ),
        f'{reverse(detail_url, args=id_news_for_args)}#comments'
    )
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    reader_client,
    comment,
    id_comment_for_args,
    edit_url,
    form_data,
    new_form_data
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    assert reader_client.post(
        reverse(edit_url, args=id_comment_for_args), data=new_form_data
    ).status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
