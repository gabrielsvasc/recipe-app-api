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

    def test_new_user_with_email_normalized(self):
        """Teste campo e-mail normalizado para usuários"""
        sample_emails = [
            ['test1@test.com', 'test1@test.com'],
            ['Test2@Test.com', 'test2@test.com'],
            ['Test3@test.com', 'test3@test.com'],
            ['test4@Test.com', 'test4@test.com'],
            ['TEST5@TEST.COM', 'test5@test.com'],
            ['TEST6@test.com', 'test6@test.com'],
            ['test7@TEST.com', 'test7@test.com'],
            ['test8@test.COM', 'test8@test.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'test123')
            self.assertEqual(user.email, expected)