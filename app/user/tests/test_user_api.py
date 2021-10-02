from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**kwargs):
    return get_user_model().obj.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """test the users API that do not require auth"""

    def setUp(self):
        self.client = APIClient()

    def test_create_validUser_success(self):
        """test creating user with valid payload"""
        payload = {
            'email': 'some@email.com',
            'password': 'password',
            'name': 'fs ls_Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().obj.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """test if the user already exists create should fail"""

        payload = {
            'email': 'some@email.com',
            'password': 'password',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_tooShort(self):
        """test if the system is rejecting if the password is too short"""
        payload = {
            'email': 'some@email.com',
            'password': 'pw',
            'name': 'fs ls_name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().obj.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)
