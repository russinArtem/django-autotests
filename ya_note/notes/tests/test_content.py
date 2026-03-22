from .base_test_case import BaseTestCase
from notes.forms import NoteForm
from notes.models import Note


class TestNotePage(BaseTestCase):
    def test_note_in_list_for_author(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок в списке
        notes, в словаре context.
        """
        self.assertIn(
            self.note,
            self.author_client.get(self.LIST_URL).context['object_list']
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_note_not_in_list_for_another_user(self):
        """
        В список заметок одного пользователя не попадают заметки
        другого пользователя.
        """
        self.assertNotIn(
            self.note,
            self.not_author_client.get(self.LIST_URL).context['object_list']
        )

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы"""
        for url in (self.ADD_URL, self.EDIT_URL):
            with self.subTest(url=url):
                form = self.author_client.get(url).context
                self.assertIn('form', form)
                self.assertIsInstance(form['form'], NoteForm)
