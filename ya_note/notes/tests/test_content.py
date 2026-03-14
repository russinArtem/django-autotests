from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotePage(TestCase):

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

    def test_notes_list_for_different_users(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок в списке
        object_list, в словаре context;
        В список заметок одного пользователя не попадают заметки
        другого пользователя.
        """
        for user, expected_result in (
            (self.author, True),
            (self.not_author, False),
        ):
            self.client.force_login(user)
            object_list = self.client.get(reverse('notes:list')).context[
                'object_list'
            ]
            with self.subTest(user=user.username):
                if expected_result:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы"""
        self.client.force_login(self.author)
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        ):
            with self.subTest(name=name):
                form = self.client.get(reverse(name, args=args)).context
                self.assertIn('form', form)
                self.assertTrue(isinstance(form['form'], NoteForm))
