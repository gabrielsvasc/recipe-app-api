"""Testa a rota de receita da API."""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Cria e retorna os detalhes de uma receita."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Cria e retorna um modelo de receita."""
    _defaults = {
        'title': 'Test Receita Titulo',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Test Description',
        'link': '',
    }
    _defaults.update(params)

    recipe = Recipe.objects.create(user=user, **_defaults)
    return recipe


def create_user(**params):
    """Cria e retorna um novo usuário."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Testes de requizições não autorizadas na API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Testa autenticação requerida na chamada da API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Testes de requizições autorizadas na API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@text.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Teste retorna uma lista de receitas."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Teste retorna uma lista de receitas limitada pelo usuário."""
        _other_user = create_user(
            email='other@test.com',
            password='otherpass123'
        )
        create_recipe(user=_other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Testa retorna os detalhes da receita."""
        _recipe = create_recipe(user=self.user)

        url = detail_url(_recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(_recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Testa a criação de uma receita."""
        payload = {
            'title': 'Test Create Recipe Success',
            'time_minutes': 1,
            'price': Decimal('1.25'),
            'description': 'Test Description Success',
        }
        res = self.client.post(RECIPES_URL, payload)
        _recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for k, v in payload.items():
            self.assertEqual(getattr(_recipe, k), v)

        self.assertEqual(_recipe.user, self.user)

    def test_recipe_detail_partial_update(self):
        """Testa a atulização de apenas um campo da receita."""
        link = 'https://test.com/example'
        _recipe = create_recipe(
            user=self.user,
            title='Teste Receita',
            link=link,
        )

        payload = {
            'title': 'Nova Receita'
        }
        url = detail_url(_recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        _recipe.refresh_from_db()

        self.assertEqual(_recipe.title, payload['title'])
        self.assertEqual(_recipe.link, link)
        self.assertEqual(_recipe.user, self.user)

    def test_recipe_detail_update(self):
        """Testa a atualização de todos os campos da receita."""
        _recipe = create_recipe(
            user=self.user,
            title='Old Receita',
            link='https://old.test',
            description='Test Old Description',
        )
        payload = {
            'title': 'Updated Test',
            'link': 'https://new.test',
            'description': 'Test New Description',
            'time_minutes': 1,
            'price': Decimal('1.50'),
        }

        url = detail_url(_recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        _recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(_recipe, k), v)
        self.assertEqual(_recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Testa alteração do usuário da receita com falha."""
        _new_user = create_user(
            email='new@test.com',
            password='new@t1234'
        )
        _recipe = create_recipe(user=self.user)

        payload = {'user': _new_user}
        url = detail_url(_recipe.id)
        self.client.patch(url, payload)

        _recipe.refresh_from_db()
        self.assertEqual(_recipe.user, self.user)

    def test_delete_recipe(self):
        """Testa o delete de uma receita."""
        _recipe = create_recipe(user=self.user)

        url = detail_url(_recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=_recipe.id).exists())

    def test_delete_other_user_recipe_error(self):
        """Testa tentativa de deletar receita de outro usuário com falha."""
        _new_user = create_user(
            email='new@test.com',
            password='new@t1234'
        )
        _recipe = create_recipe(user=_new_user)

        url = detail_url(_recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=_recipe.id).exists())