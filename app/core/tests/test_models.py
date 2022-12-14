"""
Tests for models.
"""
from unittest.mock import patch

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='email@domain.com', password='pass1234'):
    """Creates a user"""
    return get_user_model().objects.create_user(email=email, password=password)


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

    def test_create_recpe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'email@gmail.com',
            'password123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='recipe title',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample receipe description.',
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test the creation of a recipe."""
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name='Tag1'
            )
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test the creation of an ingredient."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient name.'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating unique image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
