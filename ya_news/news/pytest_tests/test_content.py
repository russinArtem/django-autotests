from news.forms import CommentForm


def test_news_count(client, home_url, news_count_on_home_page, multiple_news):
    """Количество новостей на главной странице — не более 10."""
    assert client.get(
        home_url).context['object_list'].count() == news_count_on_home_page


def test_news_order(client, home_url, multiple_news):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка
    """
    all_dates = [news.date for news in client.get(
        home_url).context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, detail_url):
    """
    Комментарии на странице отдельной новости отсортированы
    от старых к новым: старые в начале списка, новые — в конце.
    """
    response = client.get(detail_url)
    assert 'news' in response.context
    all_timestamps = [comment.created for comment in response.context[
        'news'].comment_set.all()]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, detail_url):
    """
    Анонимному пользователю не видна форма для отправки комментария
    на странице отдельной новости.
    """
    assert 'form' not in client.get(detail_url).context


def test_authorized_client_has_form(author_client, detail_url):
    """
    Авторизованному пользователю видна форма для отправки комментария
    на странице отдельной новости.
    """
    assert isinstance(
        author_client.get(detail_url).context.get('form'),
        CommentForm
    )
