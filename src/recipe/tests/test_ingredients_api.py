"""Testes para a rota Ingredients da API."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@example.com', password='testpass123'):
    """Cria e retorna um novo usuário."""

    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user, name):
    """Cria e retorna uma nova receita."""
    ingredient = Ingredient.objects.create(user=user, name=name)

    return ingredient


class PublicIngredientsApiTests(TestCase):
    """Testes de requisições não autorizadas."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Testa autenticação necessária para a rota Ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Testes de requisições autorizadas."""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Testa o retorno de uma lista com os ingredientes."""
        create_ingredient(user=self.user, name='Açucar')
        create_ingredient(user=self.user, name='Sal')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Testa o retorno da lista de ingredientes
        limitada ao usuário."""
        user2 = create_user(email='user2@test.com')
        create_ingredient(user=user2, name='Sal')
        ingredient = create_ingredient(user=self.user, name='Pimenta')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
