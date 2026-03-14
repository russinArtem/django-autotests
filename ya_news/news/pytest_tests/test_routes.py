from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        (lf('detail_url'), lf('id_news_for_args')),
        (lf('home_url'), None),
        (lf('signup_url'), None),
        (lf('login_url'), None),
    ),
)
def test_pages_availability(client, name, args):
    """
    Анонимному пользователю доступны: главная страница, страница отдельной
    новости, страницы регистрации пользователей и входа в учётную запись.
    """
    assert client.get(reverse(name, args=args)).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('author_client'), HTTPStatus.OK),
        (lf('reader_client'), HTTPStatus.NOT_FOUND),
    ],
)
@pytest.mark.parametrize(
    'name',
    (lf('edit_url'), lf('delete_url')),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, name, id_comment_for_args, expected_status
):
    """
    Страницы удаления и редактирования комментария доступны автору
    комментария.
    Авторизованный пользователь не может зайти на страницу редактирования или
    удаления чужих комментариев (возвращается ошибка 404).
    """
    assert parametrized_client.get(
        reverse(name, args=id_comment_for_args)
    ).status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (lf('edit_url'), lf('delete_url')),
)
def test_redirect_for_anonymous_client(
    client, name, id_comment_for_args, login_url
):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    url = reverse(name, args=id_comment_for_args)
    assertRedirects(client.get(url), f'{reverse(login_url)}?next={url}')
