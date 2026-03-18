from http import HTTPStatus

from .base_test_case import BaseTestCase


class TestRoutes(BaseTestCase):
    def test_pages_availability(self):
        """
        Главная страница доступна анонимному пользователю.
        Страницы регистрации пользователей, входа в учётную запись и выхода из
        неё доступны всем пользователям.
        Аутентифицированному пользователю доступны страницы:
        со списком заметок, успешного добавления заметки и
        добавления новой заметки.
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается зайти
        другой пользователь — вернётся ошибка 404.
        """
        for url, client, expected_status in [
            [self.HOME_URL, self.client, HTTPStatus.OK],
            [self.LOGIN_URL, self.client, HTTPStatus.OK],
            [self.SIGNUP_URL, self.client, HTTPStatus.OK],
            [self.LOGOUT_URL, self.client, HTTPStatus.OK],
            [self.LIST_URL, self.not_author_client, HTTPStatus.OK],
            [self.ADD_URL, self.not_author_client, HTTPStatus.OK],
            [self.SUCCESS_URL, self.not_author_client, HTTPStatus.OK],
            [self.DETAIL_URL, self.author_client, HTTPStatus.OK],
            [self.EDIT_URL, self.author_client, HTTPStatus.OK],
            [self.DELETE_URL, self.author_client, HTTPStatus.OK],
            [self.DETAIL_URL, self.not_author_client, HTTPStatus.NOT_FOUND],
            [self.EDIT_URL, self.not_author_client, HTTPStatus.NOT_FOUND],
            [self.DELETE_URL, self.not_author_client, HTTPStatus.NOT_FOUND],
        ]:
            with self.subTest(
                url=url, client=client, expected_status=expected_status
            ):
                if url == self.LOGOUT_URL:
                    response = client.post(url)
                else:
                    response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects(self):
        """
        Анонимный пользователь перенаправляется на страницу логина
        при попытке перейти на страницы: списка заметок, успешного добавления
        записи, добавления заметки, отдельной заметки, редактирования или
        удаления заметки.
        """
        for url in (
            self.LIST_URL,
            self.ADD_URL,
            self.SUCCESS_URL,
            self.DETAIL_URL,
            self.EDIT_URL,
            self.DELETE_URL,
        ):
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    f'{self.LOGIN_URL}?next={url}'
                )
