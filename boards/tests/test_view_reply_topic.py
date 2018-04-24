# coding: utf-8

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..forms import PostForm
from ..models import Board, Topic, Post
from ..views import ReplyPostView


class ReplyTopicTestCase(TestCase):
    def setUp(self):
        self.board = Board.objects.create(
            name='Django',
            description='Django board.'
        )
        self.username = 'John'
        self.password = '123456'
        user = User.objects.create_user(
            username=self.username,
            email='John@example.com',
            password=self.password
        )
        self.topic = Topic.objects.create(
            subject='Hello, World!',
            board=self.board,
            starter=user
        )
        Post.objects.create(
            message='Hello, Python!',
            topic=self.topic,
            created_by=user
        )
        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{}?next={}'.format(login_url, self.url))


class ReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func.view_class, ReplyPostView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PostForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)


class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'Hello, Python'})

    def test_redirection(self):
        url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        topic_posts_url = '{url}?page=1#2'.format(url=url)
        self.assertRedirects(self.response, topic_posts_url)

    def test_reply_created(self):
        self.assertTrue(Post.objects.count(), 2)


class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
