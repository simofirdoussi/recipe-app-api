"""
Tests for recipe APIs.
"""
from decimal import Decimal
from PIL import Image
import tempfile
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def recipe_detail_url(recipe_id):
    """Detail recipe url."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params):
    """Creates a user."""
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated recipe APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_recipe(self):
        """Test auth is required for recipe APIs."""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated recipe APIs."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes limited to an authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password1234'
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_detail_retrieve(self):
        """Test detail recipe limited to an authenticated user."""
        recipe = create_recipe(user=self.user)
        res = self.client.get(recipe_detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_api(self):
        """Test the creation of the recipe through the creation endpoint."""
        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 22,
            'price': Decimal('5.25'),
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test the partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {'title': 'New recipe title'}
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test the full update of a recipe object."""
        payload = {
            'title': 'Sample recipe title update',
            'time_minutes': 50,
            'price': Decimal('20.25'),
            'description': 'Sample description update',
            'link': 'http://example.com/recipe_update.pdf',
        }
        recipe = create_recipe(user=self.user)
        url = recipe_detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test returns error when changing the user of a recipe."""
        recipe = create_recipe(user=self.user)
        other_user = create_user(
            email='other@example.com',
            password='password1234',
        )
        payload = {
            'user': other_user,
        }

        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        self.assertNotEqual(recipe.user, other_user)

    def test_delete_recipe(self):
        """Test the deletion of a recipe."""
        recipe = create_recipe(user=self.user)
        url = recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe(self):
        """Test deleting other users recipe error."""
        other_user = create_user(
            email='email@exple.com',
            password='pass1234@',
        )
        recipe = create_recipe(user=other_user)
        url = recipe_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                user=self.user,
                name=tag['name']
            )
            self.assertTrue(exists)

    def test_create_recipe_for_existing_tags(self):
        """Test creating a new recipe with existing tags."""
        tag = Tag.objects.create(user=self.user, name='tag name')
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'tag name'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                user=self.user,
                name=tag['name']
            )
            self.assertTrue(exists)

    def test_create_tag_for_recipe_on_update(self):
        """Test creating tags when updating a recipe object."""
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{'name': 'lunch'}]
        }
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(name='lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipe tags."""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_creat_recipe_with_new_ingredient(self):
        """Test create recipe with new ingredient."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
            'ingredients': [{'name': 'Ingredient'},
                            {'name': 'Not Ingredient'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for v in payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=v['name'],
            )
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a recipe with existing ingredients."""
        ingredient = Ingredient.objects.create(user=self.user,
                                               name='Ingredient')
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
            'ingredients': [{'name': 'Ingredient'},
                            {'name': 'Not Ingredient'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for v in payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=v['name'],
            )
            self.assertTrue(exists)

    def test_create_ingredient_for_recipe_on_update(self):
        """Test creating an ingredient for recipe on update."""
        recipe = create_recipe(user=self.user)
        payload = {
            'title': 'Thai Prawn Curry',
            'ingredients': [{'name': 'Ingredient'},
                            {'name': 'Not Ingredient'}],
        }
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 2)
        for v in payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=v['name'],
            )
            self.assertTrue(exists)

    def test_update_recipe_assign_ingredient(self):
        """Test updating recipe's assigned ingredients."""
        ingredient = Ingredient.objects.create(user=self.user,
                                               name='Ingredient name')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {
            'ingredients': [{'name': 'Ingredient'},
                            {'name': 'Not Ingredient'}],
        }
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 2)

        for v in payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=v['name'],
            )
            self.assertTrue(exists)

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients."""
        ingredient1 = Ingredient.objects.create(user=self.user,
                                                name='Ingredient name')

        ingredient2 = Ingredient.objects.create(user=self.user,
                                                name='Ingredient name')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1, ingredient2)

        payload = {'ingredients': []}
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_recipe_tags_filtering(self):
        """Test filtering the recipes by tags."""
        recipe1 = create_recipe(user=self.user, title='recipe 1')
        recipe2 = create_recipe(user=self.user, title='recipe 2')
        tag1 = Tag.objects.create(name='tag1', user=self.user)
        tag2 = Tag.objects.create(name='tag2', user=self.user)
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = create_recipe(user=self.user, title='recipe 3')

        params = {'tags': f'{tag1.id}, {tag2.id}'}
        res = self.client.get(RECIPE_URL, params)

        r1 = RecipeSerializer(recipe1)
        r2 = RecipeSerializer(recipe2)
        r3 = RecipeSerializer(recipe3)

        self.assertIn(r1.data, res.data)
        self.assertIn(r2.data, res.data)
        self.assertNotIn(r3.data, res.data)

    def test_recipe_ingredients_filtering(self):
        """Test filtering recipes by ingredient."""
        recipe1 = create_recipe(user=self.user, title='recipe 1')
        recipe2 = create_recipe(user=self.user, title='recipe 2')
        ingredient1 = Ingredient.objects.create(user=self.user,
                                                name='ingredient 1')
        ingredient2 = Ingredient.objects.create(user=self.user,
                                                name='ingredient 2')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = create_recipe(user=self.user, title='recipe 3')

        params = {'ingredients': f'{ingredient1.id}, {ingredient2.id}'}
        res = self.client.get(RECIPE_URL, params)

        r1 = RecipeDetailSerializer(recipe1)
        r2 = RecipeDetailSerializer(recipe2)
        r3 = RecipeDetailSerializer(recipe3)

        self.assertIn(r1.data, res.data)
        self.assertIn(r2.data, res.data)
        self.assertNotIn(r3.data, res.data)


class TestUploadImage(TestCase):
    """Unit tests for recipe image upload."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='other@example.com',
            password='password1234',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_recipe(self):
        """Testing the upload of a recipe image."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
