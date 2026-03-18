from http import HTTPStatus

from pytils.translit import slugify

from .base_test_case import BaseTestCase
from notes.forms import WARNING
from notes.models import Note


class TestNoteManagement(BaseTestCase):
    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку"""
        initial_count = Note.objects.count()
        self.assertRedirects(
            self.author_client.post(self.ADD_URL, data=self.form_data),
            self.SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        initial_notes = list(Note.objects.all())
        self.assertRedirects(
            self.client.post(self.ADD_URL, data=self.form_data),
            f'{self.LOGIN_URL}?next={self.ADD_URL}'
        )
        self.assertEqual(initial_notes, list(Note.objects.all()))

    def test_slug_uniqueness_validation(self):
        """Невозможно создать две заметки с одинаковым slug"""
        initial_notes = list(Note.objects.all())
        self.form_data['slug'] = self.note.slug
        self.assertFormError(
            form=self.author_client.post(
                self.ADD_URL, data=self.form_data
            ).context['form'],
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(initial_notes, list(Note.objects.all()))

    def test_automatic_slug_generation(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify
        """
        initial_count = Note.objects.count()
        self.form_data.pop('slug')
        self.assertRedirects(
            self.author_client.post(self.ADD_URL, data=self.form_data),
            self.SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку"""
        self.assertRedirects(
            self.author_client.post(self.EDIT_URL, data=self.form_data),
            self.SUCCESS_URL
        )
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_not_author_cant_edit_note(self):
        """
        Зарегистрированный пользователь не может редактировать
        чужую заметку
        """
        self.assertEqual(
            self.not_author_client.post(
                self.EDIT_URL, data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку"""
        initial_count = Note.objects.count()
        self.assertRedirects(
            self.author_client.post(self.DELETE_URL),
            self.SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_not_author_cant_delete_note(self):
        """Зарегистрированный пользователь не может удалить чужую заметку"""
        initial_notes = list(Note.objects.all())
        self.assertEqual(
            self.not_author_client.post(self.DELETE_URL).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(initial_notes, list(Note.objects.all()))
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)
