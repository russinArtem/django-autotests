from .base_test_case import BaseTestCase


class TestRoutes(BaseTestCase):
    def test_pages_availability(self):
        response_code_test_cases = [
            [self.HOME_URL, self.client.get, self.OK],
            [self.LOGIN_URL, self.client.get, self.OK],
            [self.SIGNUP_URL, self.client.get, self.OK],
            [self.LOGOUT_URL, self.client.post, self.OK],
            [self.LIST_URL, self.not_author_client.get, self.OK],
            [self.ADD_URL, self.not_author_client.get, self.OK],
            [self.SUCCESS_URL, self.not_author_client.get, self.OK],
            [self.DETAIL_URL, self.author_client.get, self.OK],
            [self.EDIT_URL, self.author_client.get, self.OK],
            [self.DELETE_URL, self.author_client.get, self.OK],
            [self.DETAIL_URL, self.not_author_client.get, self.NOT_FOUND],
            [self.EDIT_URL, self.not_author_client.get, self.NOT_FOUND],
            [self.DELETE_URL, self.not_author_client.get, self.NOT_FOUND],
            [self.LIST_URL, self.client.get, self.FOUND],
            [self.ADD_URL, self.client.get, self.FOUND],
            [self.SUCCESS_URL, self.client.get, self.FOUND],
            [self.DETAIL_URL, self.client.get, self.FOUND],
            [self.EDIT_URL, self.client.get, self.FOUND],
            [self.DELETE_URL, self.client.get, self.FOUND],
        ]
        for url, method, expected_status in response_code_test_cases:
            with self.subTest(
                url=url, method=method, expected_status=expected_status
            ):
                self.assertEqual(method(url).status_code, expected_status)

    def test_redirects(self):
        """
        Анонимный пользователь перенаправляется на страницу логина
        при попытке перейти на страницы: списка заметок, успешного добавления
        записи, добавления заметки, отдельной заметки, редактирования или
        удаления заметки.
        """
        for url, redirect_url in [
            (self.LIST_URL, self.LOGIN_REDIRECT_LIST),
            (self.ADD_URL, self.LOGIN_REDIRECT_ADD),
            (self.SUCCESS_URL, self.LOGIN_REDIRECT_SUCCESS),
            (self.DETAIL_URL, self.LOGIN_REDIRECT_DETAIL),
            (self.EDIT_URL, self.LOGIN_REDIRECT_EDIT),
            (self.DELETE_URL, self.LOGIN_REDIRECT_DELETE),
        ]:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    redirect_url
                )
