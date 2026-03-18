from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

LOGIN_URL = lf('login_url')
SIGNUP_URL = lf('signup_url')
HOME_URL = lf('home_url')
DETAIL_URL = lf('detail_url')
EDIT_URL = lf('edit_url')
DELETE_URL = lf('delete_url')
CLIENT = lf('client')
AUTHOR_CLIENT = lf('author_client')
READER_CLIENT = lf('reader_client')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    [
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, READER_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, READER_CLIENT, HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_availability(parametrized_client, url, expected_status):
    """
    Анонимному пользователю доступны: главная страница, страница отдельной
    новости, страницы регистрации пользователей и входа в учётную запись.
    Страницы удаления и редактирования комментария доступны автору
    комментария.
    Авторизованный пользователь не может зайти на страницу редактирования или
    удаления чужих комментариев (возвращается ошибка 404).
    """
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL),
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    assertRedirects(client.get(url), f'{login_url}?next={url}')
