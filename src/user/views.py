"""Views para a rota User da API."""

from rest_framework import generics
from user.serializers import UserSerializer


class CreateuserView(generics.CreateAPIView):
    """Cria um usuário no sistema."""
    serializer_class = UserSerializer
