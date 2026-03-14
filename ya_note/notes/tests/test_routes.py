from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability_for_anonymous_user(self):
        """
        Главная страница доступна анонимному пользователю.
        Страницы регистрации пользователей, входа в учётную запись и выхода из
        неё доступны всем пользователям.
        """
        for name in (
            'notes:home',
            'users:login',
            'users:signup',
            'users:logout',
        ):
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Аутентифицированному пользователю доступны страницы:
        со списком заметок, успешного добавления заметки и
        добавления новой заметки.
        """
        self.client.force_login(self.not_author)
        for name, args in (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=args)).status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_for_different_users(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается зайти
        другой пользователь — вернётся ошибка 404.
        """
        for user, status in (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND),
        ):
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    self.assertEqual(
                        self.client.get(reverse(
                            name, args=(self.note.slug,))).status_code,
                        status
                    )

    def test_redirects(self):
        """
        Анонимный пользователь перенаправляется на страницу логина
        при попытке перейти на страницы: списка заметок, успешного добавления
        записи, добавления заметки, отдельной заметки, редактирования или
        удаления заметки.
        """
        for name, args in (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.assertRedirects(
                    self.client.get(url),
                    f'{reverse('users:login')}?next={url}'
                )
