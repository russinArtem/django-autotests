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
LOGIN_REDIRECT_EDIT = lf('login_redirect_edit')
LOGIN_REDIRECT_DELETE = lf('login_redirect_delete')
OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    [
        (DETAIL_URL, CLIENT, OK),
        (HOME_URL, CLIENT, OK),
        (SIGNUP_URL, CLIENT, OK),
        (LOGIN_URL, CLIENT, OK),
        (EDIT_URL, AUTHOR_CLIENT, OK),
        (DELETE_URL, AUTHOR_CLIENT, OK),
        (EDIT_URL, READER_CLIENT, NOT_FOUND),
        (DELETE_URL, READER_CLIENT, NOT_FOUND),
        (EDIT_URL, CLIENT, FOUND),
        (DELETE_URL, CLIENT, FOUND),
    ]
)
def test_pages_availability(parametrized_client, url, expected_status):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url, login_redirect_url',
    [
        (EDIT_URL, LOGIN_REDIRECT_EDIT),
        (DELETE_URL, LOGIN_REDIRECT_DELETE),
    ]
)
def test_redirect_for_anonymous_client(client, url, login_redirect_url):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    assertRedirects(client.get(url), login_redirect_url)
