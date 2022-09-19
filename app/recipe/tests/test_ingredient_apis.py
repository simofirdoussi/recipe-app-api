"""
Ingredient API test cases.
"""
from django.test import TestCase
from django.urls import reverse
from core.models import Ingredient
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='user@gmail.com', password='pass12343'):
    """Create a user instance."""
    return get_user_model().objects.create_user(
        email=email,
        password=password,
    )


def create_ingredient(user, name):
    """Returns an ingredient """
    return Ingredient.objects.create(user=user, name=name)


def detail_ingredient(ingredient_id):
    """Returns the detial URL of an ingredient."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientAPITest(TestCase):
    """Public ingredient API tests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Auth required testing."""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    """Private ingredient API tests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Testing the retrieval of ingredients."""
        create_ingredient(self.user, 'ingredient n')
        create_ingredient(self.user, 'ingredient nn')

        res = self.client.get(INGREDIENTS_URL)

        tags = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ingredient_user_specific(self):
        """Test retrieving ingredient for a specific user."""

        other_user = create_user(
            email='other@mail.com',
            password='otherpass123',
        )
        create_ingredient(user=other_user, name='ingredient 3')
        create_ingredient(user=self.user, name='ingredient 1')
        create_ingredient(user=self.user, name='ingredient 2')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.filter(
                                                user=self.user
                                                ).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient(self):
        """Test updating ingredient."""
        ingredient = create_ingredient(
            user=self.user,
            name='ingredient name'
        )
        payload = {
            'name': 'updated ingredient name.'
        }
        url = detail_ingredient(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.user, self.user)

    def test_delete_ingredient(self):
        """Test delete an ingredient object."""
        ingredient = create_ingredient(
            user=self.user,
            name='ingredient name'
        )
        url = detail_ingredient(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id))
