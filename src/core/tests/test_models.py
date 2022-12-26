"""
  Teste para os models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch
from decimal import Decimal

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Cria e retorna um novo usuário."""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_tag(self):
        """Testa a criação do model da Tag com cucesso."""
        _user = create_user()
        tag = models.Tag.objects.create(user=_user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Testa a criação do model da rota Ingredient."""
        _user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=_user,
            name='Ingrediente Teste'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Testa a geração do path da imagem."""
        _uuid = 'test-uuid'
        mock_uuid.return_value = _uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{_uuid}.jpg')
