"""Serializer para a rota de receitas da API"""

from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer para as receitas."""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer para o detalhamento das receitas."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer para a rota de Tag."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
