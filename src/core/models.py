from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Gerenciador de usuário"""

    def create_user(self, email, password=None, **extra_fields):
        """Cria, salava e retorna novo usuário"""
        if not email:
            raise ValueError('ERRO: Usuário precisa ter um E-mail!')

        user = self.model(email=self.normalize_email(
            email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuário"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
