from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    OK = HTTPStatus.OK
    NOT_FOUND = HTTPStatus.NOT_FOUND
    FOUND = HTTPStatus.FOUND
    NOTE_SLUG = 'note-slug'
    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    SIGNUP_URL = reverse('users:signup')
    LOGOUT_URL = reverse('users:logout')
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')
    DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
    EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
    DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
    LOGIN_REDIRECT_LIST = f'{LOGIN_URL}?next={LIST_URL}'
    LOGIN_REDIRECT_ADD = f'{LOGIN_URL}?next={ADD_URL}'
    LOGIN_REDIRECT_SUCCESS = f'{LOGIN_URL}?next={SUCCESS_URL}'
    LOGIN_REDIRECT_DETAIL = f'{LOGIN_URL}?next={DETAIL_URL}'
    LOGIN_REDIRECT_EDIT = f'{LOGIN_URL}?next={EDIT_URL}'
    LOGIN_REDIRECT_DELETE = f'{LOGIN_URL}?next={DELETE_URL}'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
