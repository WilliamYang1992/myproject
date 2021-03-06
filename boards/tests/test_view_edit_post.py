# coding: utf-8

from django.contrib.auth.models import User
from django.forms import ModelForm
from django.test import TestCase
from django.urls import reverse, resolve

from ..models import Board, Topic, Post
from ..views import PostUpdateView


class PostUpdateViewTestCase(TestCase):
    def setUp(self):
        self.username = 'John'
        self.email = 'John@example.com'
        self.password = '123456'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        self.board = Board.objects.create(
            name='Django',
            description='Django board.'
        )
        self.topic = Topic.objects.create(
            subject='Hello world!',
            board=self.board,
            starter=self.user
        )
        self.post = Post.objects.create(
            message='Hello, Python!',
            topic=self.topic,
            created_by=self.user
        )
        self.url = reverse('edit_post', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk,
            'post_pk': self.post.pk
        })


class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{}?next={}'.format(login_url, self.url))


class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super(UnauthorizedPostUpdateViewTests, self).setUp()
        username = 'Jane'
        password = '654321'
        email = 'Jane@example.com'
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 404)


class PostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super(PostUpdateViewTests, self).setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/boards/1/topics/1/posts/1/edit/')
        self.assertEquals(view.func.view_class, PostUpdateView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, ModelForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)


class SuccessfulPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super(SuccessfulPostUpdateViewTests, self).setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'edited message'})

    def test_redirection(self):
        topic_posts_url = reverse('topic_posts', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk
        })
        self.assertRedirects(self.response, topic_posts_url)

    def test_post_changed(self):
        self.post.refresh_from_db()
        self.assertEquals(self.post.message, 'edited message')


class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super(InvalidPostUpdateViewTests, self).setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)


class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super(InvalidPostUpdateViewTests, self).setUp()
