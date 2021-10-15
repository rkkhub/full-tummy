from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

        def test_create_authToken(self):
            """Test that a token is created for user"""
            payload = {'email': 'test@email.com', 'password': 'test123'}
            create_user(**payload)
            res = self.client.post(TOKEN_URL, payload)

            self.assertIn('token', res.data)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

        def test_createToken_invalidCreds(self):
            """token should not be created if the credentials are invalid"""
            payload = {'email': 'test@email.com', 'password': 'test123'}
            create_user(**payload)

            test_payload = {'email': 'test@email.com',
                            'password': 'diffetentpwd'}
            res = self.client.post(TOKEN_URL, test_payload)

            self.assertNotIn('token', res.data)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        def test_createToken_nonExistUser(self):
            """test the token is not created if the user does not exist"""
            payload = {'email': 'test@email.com', 'password': 'test123'}
            res = self.client.post(TOKEN_URL, payload)

            self.assertNotIn('token', res.data)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        def test_createToken_missingPass(self):
            """test that the email and passowrd are
            required fields to create token"""
            payload = {'email': 'test', 'password': ''}
            res = self.client.post(TOKEN_URL, payload)

            self.assertNotIn('token', res.data)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        def test_retrieve_user_unauthorized(self):
            """Auth is required for users"""
            res = self.client.get(ME_URL)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """"Test APi requests that require authentication"""

    def setUp(self):
        self.user = create_user(email='test@email.com',
                                password='12345678',
                                name='name')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_profile_sucess(self):
        """Test retrieving for loggedin user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """test that the post is not allowed on the me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """test updating the user profile"""
        payload = {'name': 'first_name', 'password': 'somepassword'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
