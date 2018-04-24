# coding: utf-8

from django.contrib.auth.models import User

from django import forms
from django.test import TestCase
from ..templatetags.form_tags import field_type, input_class
from ..templatetags.gravatar import gravatar


class ExampleForm(forms.Form):
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        fields = ('name', 'password')


class FieldTypeTests(TestCase):
    def test_field_widget_type(self):
        form = ExampleForm()
        self.assertEquals('TextInput', field_type(form['name']))
        self.assertEquals('PasswordInput', field_type(form['password']))


class InputClassTests(TestCase):
    def test_unbound_field_initial_state(self):
        form = ExampleForm()
        self.assertEquals('form-control', input_class(form['name']))

    def test_valid_bound_field(self):
        form = ExampleForm({
            'name': 'John',
            'password': 'Qq123456'
        })
        self.assertEquals('form-control is-valid', input_class(form['name']))
        self.assertEquals('form-control', input_class(form['password']))

    def test_invalid_bound_field(self):
        form = ExampleForm({
            'name': '',
            'password': 'Qq123456'
        })
        self.assertEquals('form-control is-invalid', input_class(form['name']))


class GravatarTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='John',
            email='John@example.com',
            password='123456'
        )

    def test_valid_input(self):
        url = gravatar(self.user)
        self.assertTrue(isinstance(url, str))
        self.assertIn('https://www.gravatar.com/avatar/', url)
