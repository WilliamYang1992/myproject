# coding: utf-8

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..models import Board, Topic, Post
from ..views import topic_posts


class TopicPostsTests(TestCase):
    def setUp(self):
        board = Board.objects.create(
            name='Django',
            description='Django board.'
        )
        user = User.objects.create_user(
            username='John',
            email='John@example.com',
            password='123456'
        )
        topic = Topic.objects.create(
            subject='Hello, World',
            board=board,
            starter=user
        )
        Post.objects.create(
            message='Hello Python',
            topic=topic,
            created_by=user
        )
        url = reverse('topic_posts', kwargs={'pk': board.pk, 'topic_pk': topic.pk})
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/')
        self.assertEquals(view.func, topic_posts)
