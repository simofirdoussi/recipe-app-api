"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """ Test models. """

    def test_create_user_with_email_successful(self):
        """ Test creating a user with email. """
        email = 'test@email.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_email(self):
        """ Testing the normalization of the email. """
        sample_emails = [
            ['test1@Example.com', 'test1@example.com'],
            ['Test2@EXAMPLE.com', 'Test2@example.com'],
            ['TEST3@Example.com', 'TEST3@example.com'],
            ['test4@Example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_user_creation_without_email(self):
        """ testing the creation of a new user without email. """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """test for creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@email.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
