"""Views para a rota User da API."""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Cria um usuário no sistema."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Cria um novo token de autenticação para o usuário."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Administra a autenticação do usuário."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Busca e retorna o usuário autenticado."""
        return self.request.user
