from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


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
def news(db):
    news = News.objects.create(
        title='Заголовок',
        text='Текст')
    return news


@pytest.fixture
def comment(db, author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    return comment


@pytest.fixture
def filling_database(db):
    """Создаем базу заполненную новостями."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments(db, news, author):
    """Создание 10 комментариев в разное время."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def url_to_comments(detail_url):
    url_to_comments = detail_url + '#comments'
    return url_to_comments


@pytest.fixture
def comment_edit_url(comment):
    comment_edit_url = reverse('news:edit', args=(comment.id,))
    return comment_edit_url


@pytest.fixture
def comment_delete_url(comment):
    comment_delete_url = reverse('news:delete', args=(comment.id,))
    return comment_delete_url


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """Сохраняем в переменную адрес страницы с новостью."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
