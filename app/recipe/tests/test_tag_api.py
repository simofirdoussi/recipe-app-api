"""
Test cases of the tag apis.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


def create_user(email='email@example.com', password='pass1234'):
    """Create a user instance."""
    return get_user_model().objects.create_user(
        email=email,
        password=password,
    )


def tag_detail_url(tag_id):
    """Returns the detail url of a specific tag."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_tag(user, **params):
    """Create and return a tag object."""
    defaults = {
        'name': 'tag name',
    }
    defaults.update(params)
    tag = Tag.objects.create(user=user, **defaults)
    return tag


class PublicTagAPITest(TestCase):
    """Test unauthenticated tag APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_recipe(self):
        """Test auth is required for recipe APIs."""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(TestCase):
    """Tes authenticated tag APIs."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        create_tag(user=self.user)
        create_tag(user=self.user)

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tags_user_special(self):
        """Test the retrieval of the users tags."""
        user2 = create_user(email='email2@mail.com', password='pass123QWe')
        create_tag(user=user2)
        create_tag(user=self.user)
        create_tag(user=self.user)

        res = self.client.get(TAG_URL)

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_tag(self):
        """Test update tags."""
        tag = create_tag(user=self.user)
        payload = {
            'name': 'tag name updated.'
        }

        url = tag_detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.user, self.user)

    def test_deleting_tag(self):
        """Test deleting tags."""
        tag = create_tag(user=self.user)
        url = tag_detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
