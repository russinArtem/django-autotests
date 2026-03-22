from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
import pytest

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(
    db,  # noqa
):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def multiple_news():
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_to_comments(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def login_redirect_edit(login_url, edit_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def login_redirect_delete(login_url, delete_url):
    return f'{login_url}?next={delete_url}'


@pytest.fixture
def login_redirect_detail(login_url, detail_url):
    return f'{login_url}?next={detail_url}'
