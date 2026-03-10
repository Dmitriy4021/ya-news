from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (lf('home_url'), lf('client'), HTTPStatus.OK),
        (lf('detail_url'), lf('client'), HTTPStatus.OK),
        (lf('login_url'), lf('client'), HTTPStatus.OK),
        (lf('signup_url'), lf('client'), HTTPStatus.OK),
        (lf('comment_edit_url'), lf('author_client'), HTTPStatus.OK),
        (lf('comment_delete_url'), lf('author_client'), HTTPStatus.OK),
        (lf('comment_edit_url'), lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('comment_delete_url'), lf('reader_client'), HTTPStatus.NOT_FOUND),

    )
)
def test_pages_and_comment_delete_edit_availability(
    parametrized_client,
    url,
    expected_status,
):
    """Проверяем доступность главной страницы."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        lf('comment_edit_url'),
        lf('comment_delete_url'),
    )
)
def test_redirect_for_anonymous_client(client, login_url, url, comment):
    """Тест редиректа для ананимных пользователей."""
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
