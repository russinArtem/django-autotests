from .base_test_case import BaseTestCase


class TestRoutes(BaseTestCase):
    def test_pages_availability(self):
        response_code_test_cases = {
            self.HOME_URL: [(self.client.get, self.OK)],
            self.LOGIN_URL: [(self.client.get, self.OK)],
            self.SIGNUP_URL: [(self.client.get, self.OK)],
            self.LOGOUT_URL: [(self.client.post, self.OK)],
            self.LIST_URL: [
                (self.not_author_client.get, self.OK),
                (self.client.get, self.FOUND),
            ],
            self.ADD_URL: [
                (self.not_author_client.get, self.OK),
                (self.client.get, self.FOUND),
            ],
            self.SUCCESS_URL: [
                (self.not_author_client.get, self.OK),
                (self.client.get, self.FOUND),
            ],
            self.DETAIL_URL: [
                (self.author_client.get, self.OK),
                (self.not_author_client.get, self.NOT_FOUND),
                (self.client.get, self.FOUND),
            ],
            self.EDIT_URL: [
                (self.author_client.get, self.OK),
                (self.not_author_client.get, self.NOT_FOUND),
                (self.client.get, self.FOUND),
            ],
            self.DELETE_URL: [
                (self.author_client.get, self.OK),
                (self.not_author_client.get, self.NOT_FOUND),
                (self.client.get, self.FOUND),
            ],
        }
        for url, response_parameters in response_code_test_cases.items():
            for client, expected_status in response_parameters:
                with self.subTest(
                    url=url, client=client, expected_status=expected_status
                ):
                    self.assertEqual(client(url).status_code, expected_status)

    def test_redirects(self):
        """
        Анонимный пользователь перенаправляется на страницу логина
        при попытке перейти на страницы: списка заметок, успешного добавления
        записи, добавления заметки, отдельной заметки, редактирования или
        удаления заметки.
        """
        for url, redirect_url in [
            (self.LIST_URL, self.LOGIN_REDIRECT_URLS['list']),
            (self.ADD_URL, self.LOGIN_REDIRECT_URLS['add']),
            (self.SUCCESS_URL, self.LOGIN_REDIRECT_URLS['success']),
            (self.DETAIL_URL, self.LOGIN_REDIRECT_URLS['detail']),
            (self.EDIT_URL, self.LOGIN_REDIRECT_URLS['edit']),
            (self.DELETE_URL, self.LOGIN_REDIRECT_URLS['delete']),
        ]:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    redirect_url
                )
