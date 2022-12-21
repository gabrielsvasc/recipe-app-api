"""Testa a rota de receita da API."""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

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

    def test_create_recipe_with_new_tags(self):
        """Testa a criação de receita com Tag nova."""
        _payload = {
            'title': 'Comida Brasileira',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Brasileira'}, {'name': 'Jantar'}],
        }
        res = self.client.post(RECIPES_URL, _payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)
        for tag in _payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Testa a criação de receita com tag existente."""
        _tag_japonesa = Tag.objects.create(
            user=self.user,
            name='Japonesa'
        )
        _payload = {
            'title': 'Temaki',
            'time_minutes': 40,
            'price': Decimal('14.50'),
            'tags': [{'name': 'Japonesa'}, {'name': 'Almoço'}],
        }

        res = self.client.post(RECIPES_URL, _payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(_tag_japonesa, recipe.tags.all())
        for tag in _payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Testa a criação de Tag durante Update na receita."""
        _recipe = create_recipe(user=self.user)

        _payload = {'tags': [{'name': 'Brasileira'}]}
        url = detail_url(_recipe.id)
        res = self.client.patch(url, _payload, format='json')
        _new_tag = Tag.objects.get(user=self.user, name='Brasileira')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(_new_tag, _recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Testa a vinculação de Tags no Update da receita."""
        _tag_brekfast = Tag.objects.create(
            user=self.user, name='Café da Manhã')
        _tag_lunch = Tag.objects.create(user=self.user, name='Lanche')
        _recipe = create_recipe(user=self.user)
        _recipe.tags.add(_tag_brekfast)

        _payload = {'tags': [{'name': 'Lanche'}]}
        url = detail_url(_recipe.id)
        res = self.client.patch(url, _payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(_tag_lunch, _recipe.tags.all())
        self.assertNotIn(_tag_brekfast, _recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Testa a remoção de todas as tags de uma receita."""
        _tag = Tag.objects.create(user=self.user, name='Brasileira')
        _recipe = create_recipe(user=self.user)
        _recipe.tags.add(_tag)

        _payload = {'tags': []}
        url = detail_url(_recipe.id)
        res = self.client.patch(url, _payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(_recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Testa a criação de receita com ingredientes novos."""
        _payload = {
            'title': 'Comida Brasileira',
            'time_minutes': 20,
            'price': Decimal('2.50'),
            'ingredients': [{'name': 'Sal'}, {'name': 'Pimenta'}],
        }

        res = self.client.post(RECIPES_URL, _payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in _payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Testa a criação de uma receita com um
        ingrediente já existente."""
        _ingredient = Ingredient.objects.create(
            user=self.user,
            name='Sal'
        )
        _payload = {
            'title': 'Temaki',
            'time_minutes': 40,
            'price': Decimal('14.50'),
            'ingredients': [{'name': 'Sal'}, {'name': 'Pimenta'}],
        }

        res = self.client.post(RECIPES_URL, _payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(_ingredient, recipe.ingredients.all())
        for ingredient in _payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Testa a criação de ingrediente durante Update na receita."""
        _recipe = create_recipe(user=self.user)
        _payload = {'ingredients': [{'name': 'Sal'}]}
        url = detail_url(_recipe.id)

        res = self.client.patch(url, _payload, format='json')
        _new_ingredient = Ingredient.objects.get(
            user=self.user, name='Sal')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(_new_ingredient, _recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Testa a vinculação de ingredientes no Update da receita."""
        _ingredient_sault = Ingredient.objects.create(
            user=self.user, name='Sal')
        _ingredient_pepper = Ingredient.objects.create(
            user=self.user, name='Pimenta')
        _recipe = create_recipe(user=self.user)
        _recipe.ingredients.add(_ingredient_sault)

        _payload = {'ingredients': [{'name': 'Sal'}]}
        url = detail_url(_recipe.id)
        res = self.client.patch(url, _payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(_ingredient_sault, _recipe.ingredients.all())
        self.assertNotIn(_ingredient_pepper, _recipe.ingredients.all())

    def test_clear_recipe_tags(self):
        """Testa a remoção de todos os ingredientes de uma receita."""
        _ingredient = Ingredient.objects.create(
            user=self.user, name='Sal')
        _recipe = create_recipe(user=self.user)
        _recipe.ingredients.add(_ingredient)

        _payload = {'ingredients': []}
        url = detail_url(_recipe.id)
        res = self.client.patch(url, _payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(_recipe.ingredients.count(), 0)
