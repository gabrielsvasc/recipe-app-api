"""
  Teste para os models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models


class ModelTests(TestCase):
    """Teste dos models"""

    def test_create_user_with_email_successful(self):
        """Teste criar um user com e-mail sucesso"""
        email_test = "test@test.com"
        password_test = "test123"
        user = get_user_model().objects.create_user(
            email=email_test,
            password=password_test,
        )

        self.assertEqual(user.email, email_test)
        self.assertTrue(user.check_password(password_test))

    def test_new_user_with_email_normalized(self):
        """Teste campo e-mail normalizado para usuários"""
        sample_emails = [
            ['test1@test.com', 'test1@test.com'],
            ['Test2@Test.com', 'test2@test.com'],
            ['Test3@test.com', 'test3@test.com'],
            ['test4@Test.com', 'test4@test.com'],
            ['TEST5@TEST.COM', 'test5@test.com'],
            ['TEST6@test.com', 'test6@test.com'],
            ['test7@TEST.com', 'test7@test.com'],
            ['test8@test.COM', 'test8@test.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'test123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Teste de usuário sem e-mail raises ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser_success(self):
        """Teste de criação de Usuário Super"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Teste de criação de receita com sucesso."""
        _user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=_user,
            title='Test Receita',
            time_minutes=5,
            price=Decimal('5.50'),
        )

        self.assertEqual(str(recipe), recipe.title)
