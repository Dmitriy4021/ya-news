from http import HTTPStatus
# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse().
from django.urls import reverse

from news.models import Comment, News

# Получаем модель пользователя.
User = get_user_model()

class TestRoutes(TestCase):
    """Тесты проверки доступности страниц."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка к тестам."""
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # От имени одного пользователя создаём комментарий к новости:
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    # def test_home_page(self):
    #     """Тест доступности главной страницы."""
    #     # Вместо прямого указания адреса
    #     # получаем его при помощи функции reverse().
    #     url = reverse('news:home') # вместо response = self.client.get('/')
    #     response = self.client.get(url)
    #     # Проверяем, что код ответа равен статусу OK (он же 200).
    #     self.assertEqual(response.status_code, HTTPStatus.OK) # вместо self.assertEqual(response.status_code, 200)

    # def test_news_detail_page(self):
    #     """Тест полной страницы новости."""

    #     url = reverse('news:detail', args=(self.news.id,))
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)

# вместо двух тестов создаем один с помощью subTest(self):

    def test_pages_availability(self):
        """Проверка доступности страниц анонимным пользователям"""
        # Создаём набор тестовых данных - кортеж кортежей.
        # Каждый вложенный кортеж содержит два элемента:
        # имя пути и позиционные аргументы для функции reverse().
        urls = (
            # Путь для главной страницы не принимает
            # никаких позиционных аргументов, 
            # поэтому вторым параметром ставим None.
            ('news:home', None),
            # Путь для страницы новости 
            # принимает в качестве позиционного аргумента
            # id записи; передаём его в кортеже.
            ('news:detail', (self.news.id,)),
            # Пути до страниц логина и регистрации
            ('users:login', None),
            ('users:signup', None),
        )
        # Итерируемся по внешнему кортежу 
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_availability_for_comment_edit_and_delete(self):
        """Тест доступа автора и не автора к ред. и удалению комментария."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('news:edit', 'news:delete'):  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=(self.comment.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status) 


    def test_redirect_for_anonymous_client(self):
        """Тест редиректа для ананимных пользователей"""
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.comment.id,))
                # Получаем ожидаемый адрес страницы логина, 
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
                