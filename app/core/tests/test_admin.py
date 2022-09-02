""" test for the django admin modifications. """

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase


class AdminSiteTests(TestCase):
    """ Tests for the django admin. """

    def setUp(self):
        """Create user and client. """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='test123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='test1234',
            name='Test User'
        )

    def test_users_list(self):
        """ Test that users are listed on page. """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """ Test edit user page works. """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
