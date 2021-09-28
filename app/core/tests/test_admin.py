from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().obj.create_superuser(
            email='admin@dev.com',
            password='password123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().obj.create_user(
            email='some@dev.com',
            password='asdf123',
            name='f_name l_name'
        )

    def test_users_lister(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_userChangePage(self):
        """Test if the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_createUserPage(self):
        """Test if the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
