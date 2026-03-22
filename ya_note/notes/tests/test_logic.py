from pytils.translit import slugify

from .base_test_case import BaseTestCase
from notes.forms import WARNING
from notes.models import Note


class TestNoteManagement(BaseTestCase):
    def create_note(self):
        notes = set(Note.objects.all())
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(response.status_code, self.FOUND)
        new_notes = set(Note.objects.all()) - notes
        self.assertEqual(len(new_notes), 1)
        return new_notes.pop()

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку"""
        new_note = self.create_note()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        notes = set(Note.objects.all())
        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.LOGIN_REDIRECT_ADD)
        self.assertEqual(response.status_code, self.FOUND)
        self.assertEqual(notes, set(Note.objects.all()))

    def test_creating_note_with_existing_slug_raises_error(self):
        """Невозможно создать две заметки с одинаковым slug"""
        self.form_data['slug'] = self.note.slug
        notes = set(Note.objects.all())
        self.assertFormError(
            form=self.author_client.post(
                self.ADD_URL, data=self.form_data
            ).context['form'],
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(notes, set(Note.objects.all()))

    def test_slug_auto_generation_when_not_provided(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify
        """
        self.form_data.pop('slug')
        new_note = self.create_note()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        """Автор может редактировать заметку"""
        response = self.author_client.post(self.EDIT_URL, data=self.form_data)
        self.assertRedirects(
            response,
            self.SUCCESS_URL
        )
        self.assertEqual(response.status_code, self.FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_not_author_cant_edit_note(self):
        """
        Зарегистрированный пользователь не может редактировать
        чужую заметку
        """
        self.assertEqual(
            self.not_author_client.post(
                self.EDIT_URL, data=self.form_data
            ).status_code,
            self.NOT_FOUND
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку"""
        initial_count = Note.objects.count()
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(response.status_code, self.FOUND)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_not_author_cant_delete_note(self):
        """Зарегистрированный пользователь не может удалить чужую заметку"""
        notes = set(Note.objects.all())
        self.assertEqual(
            self.not_author_client.post(self.DELETE_URL).status_code,
            self.NOT_FOUND
        )
        self.assertEqual(notes, set(Note.objects.all()))
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)
