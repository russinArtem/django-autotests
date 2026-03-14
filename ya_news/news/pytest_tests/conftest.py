from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test.client import Client

from news.forms import BAD_WORDS
from news.models import Comment, News


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
def news_count_on_home_page():
    return settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def multiple_news(db, news_count_on_home_page):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(news_count_on_home_page + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment_text():
    return 'Текст комментария'


@pytest.fixture
def new_comment_text():
    return 'Обновлённый комментарий'


@pytest.fixture
def comment(news, author, comment_text):
    return Comment.objects.create(
        news=news,
        author=author,
        text=comment_text
    )


@pytest.fixture
def form_data(comment_text):
    return {'text': comment_text}


@pytest.fixture
def new_form_data(new_comment_text):
    return {'text': new_comment_text}


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def id_news_for_args(news):
    return (news.id,)


@pytest.fixture
def id_comment_for_args(comment):
    return (comment.id,)


@pytest.fixture
def login_url():
    return 'users:login'


@pytest.fixture
def signup_url():
    return 'users:signup'


@pytest.fixture
def home_url():
    return 'news:home'


@pytest.fixture
def detail_url():
    return 'news:detail'


@pytest.fixture
def edit_url():
    return 'news:edit'


@pytest.fixture
def delete_url():
    return 'news:delete'
