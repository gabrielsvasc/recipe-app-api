"""Testa a rota de Tag da API."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe
)

from recipe.serializers import TagSerializer

from decimal import Decimal


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Cria e retorna uma url de tag detalhada."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Cria e retorna um novo usuário."""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """Testa requisições não autenticadas."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Teste retorna HTTT_401 para usuário não autenticado. """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Testa requisições autenticadas."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Teste retorna lista de tags."""
        Tag.objects.create(user=self.user,  name='Brasileira')
        Tag.objects.create(user=self.user,  name='Japonesa')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Teste retorna lista de tags limitado ao usuário."""
        _user2 = create_user(email='user2@test.com')
        Tag.objects.create(user=_user2,  name='Tailandesa')
        tag = Tag.objects.create(user=self.user,  name='Japonesa')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Testa a atualização do nome de uma tag."""
        tag = Tag.objects.create(user=self.user, name='Dinner')

        payload = {
            'name': 'Dessert'
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Testa o delete de uma tag existente."""
        tag = Tag.objects.create(user=self.user, name='Delete Tag')

        url = detail_url(tag.id)
        res = self.client.delete(url)
        tags = Tag.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Testa a listagem de tags atreladas a uma receita."""
        tag1 = Tag.objects.create(user=self.user, name='Almoço')
        tag2 = Tag.objects.create(user=self.user, name='Janta')
        recipe = Recipe.objects.create(
            title='Carne Assada',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Testa a filtragem apenas de tags e as retorna em uma lista."""
        tag = Tag.objects.create(user=self.user, name='Almoço')
        Tag.objects.create(user=self.user, name='Janta')
        recipe1 = Recipe.objects.create(
            title='Carne Assada',
            time_minutes=15,
            price=Decimal('20.50'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Carne Moida',
            time_minutes=10,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
