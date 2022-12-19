"""Testa a rota de Tag da API."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


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
