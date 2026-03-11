from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def test_anonymous_user_cant_create_comment(
        client,
        detail_url,
):
    """Проверка POST-запросов на добавление комментариев анонимом"""
    form_data = {'text': COMMENT_TEXT}
    first_comments_count = Comment.objects.count()
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == first_comments_count


def test_user_can_create_comment(
        author_client,
        detail_url,
        news,
        author,
):
    """Проверка POST-запросов на добавление комментариев автооризованым"""
    Comment.objects.all().delete()
    form_data = {'text': COMMENT_TEXT}
    first_comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == first_comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(
        author_client,
        detail_url,
        bad_word,
):
    """Проверка исключения плохих слов в комментарии"""
    first_comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    form = response.context['form']
    comments_count = Comment.objects.count()
    assert comments_count == first_comments_count
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
        author_client,
        comment_delete_url,
        url_to_comments
):
    """Тест на возможность удаления комментария автором."""
    first_comments_count = Comment.objects.count()
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == first_comments_count - 1


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        comment_delete_url
):
    """Тест на возможность удаления коммента другим пользователем."""
    first_comments_count = Comment.objects.count()
    response = reader_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == first_comments_count


def test_author_can_edit_comment(
        author_client,
        comment_edit_url,
        url_to_comments,
        comment,
):
    """Тест на возможность редактирования автором."""
    new_form_data = {'text': NEW_COMMENT_TEXT}
    response = author_client.post(comment_edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment_new = Comment.objects.get(id=comment.id)
    assert comment_new.text == new_form_data['text']
    assert comment_new.author == comment.author
    assert comment_new.news == comment.news


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment_edit_url,
        comment,
):
    """Тест на возможность редактирования другим пользователем."""
    new_form_data = {'text': NEW_COMMENT_TEXT}
    response = reader_client.post(comment_edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_new = Comment.objects.get(id=comment.id)
    assert comment_new.text == comment.text
    assert comment_new.author == comment.author
    assert comment_new.news == comment.news
