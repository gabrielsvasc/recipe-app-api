""" Teste para a aba de usuários da API API. """

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Cria e retorna um novo usuário"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Testa as features públicas da API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Testa criar um usuário com sucesso """
        payload = {
            'email': 'test@test.com',
            'password': 'test123',
            'name': 'Test Test',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Testa criação de usuário com e-mail existente"""
        payload = {
            'email': 'test@test.com',
            'password': 'test123',
            'name': 'Test Test',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Testa criação de usuário com senha menor que 5 caracteres"""
        payload = {
            'email': 'test2@test.com',
            'password': 'pw',
            'name': 'Test Test',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
