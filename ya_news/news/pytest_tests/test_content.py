import pytest

from django.urls import reverse

from news.forms import CommentForm


def test_news_count(client, home_url, news_count_on_home_page, multiple_news):
    """Количество новостей на главной странице — не более 10."""
    assert client.get(reverse(
        home_url)).context['object_list'].count() == news_count_on_home_page


def test_news_order(client, home_url, multiple_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка
    """
    all_dates = [news.date for news in client.get(
        reverse(home_url)).context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, id_news_for_args, detail_url):
    """
    Комментарии на странице отдельной новости отсортированы
    от старых к новым: старые в начале списка, новые — в конце.
    """
    response = client.get(reverse(detail_url, args=id_news_for_args))
    assert 'news' in response.context
    all_timestamps = [comment.created for comment in response.context[
        'news'].comment_set.all()]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_news_for_args, detail_url):
    """
    Анонимному пользователю не видна форма для отправки комментария
    на странице отдельной новости.
    """
    assert 'form' not in client.get(
        reverse(detail_url, args=id_news_for_args)).context


@pytest.mark.django_db
def test_authorized_client_has_form(
    author_client, id_news_for_args, detail_url
):
    """
    Авторизованному пользователю видна форма для отправки комментария
    на странице отдельной новости.
    """
    response = author_client.get(reverse(detail_url, args=id_news_for_args))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
