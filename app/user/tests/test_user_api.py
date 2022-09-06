"""
Tests for the user api.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testing1234',
            'name': 'Jhon Doe',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned is user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testing1234',
            'name': 'Jhon Doe',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error is returned if password is too short."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test creating a token for user given valid creds."""
        user_details = {
            'name': 'Name test',
            'email': 'email@gmail.com',
            'password': 'test-pw-user-123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_ok)

    def test_create_token_bad_creds(self):
        """Test returns error if creds are invalid."""
        user_details = {
            'name': 'Name test',
            'email': 'email@gmail.com',
            'password': 'test-pw-user-123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'somthing',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)

    def test_create_token_blank_password(self):
        """Test returns error if password is empty."""
        user_details = {
            'name': 'Name test',
            'email': 'email@gmail.com',
            'password': '',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'somthing',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)
