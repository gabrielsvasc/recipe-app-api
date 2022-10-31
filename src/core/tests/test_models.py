"""
  Testa para os models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


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
