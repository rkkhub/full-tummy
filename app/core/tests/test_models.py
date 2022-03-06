from core import models
from django.test import TestCase
from django.contrib.auth import get_user_model

default_email = "rkkmailbox@gmail.com"
default_pass = "test123456"


def sample_user(email="test@fulltummy.com", password="test123456"):
    """Create a sample user"""
    return get_user_model().obj.create_user(email, password)


class ModelTests(TestCase):

    def test_createUser_withEmail_success(self):
        "Testing create a new user with an email is successfull"
        user = get_user_model().obj.create_user(email=default_email,
                                                password=default_pass)

        self.assertEqual(user.email, default_email)
        self.assertTrue(user.check_password(default_pass))

    def test_userEmail_normalized(self):
        """test if the email for a new user is normalized"""
        email = 'test@GMAIL.COM'
        user = get_user_model().obj.create_user(email, password='test123')

        self.assertEqual(user.email, email.lower())

    def test_userEmail_emptyNotAllowed(self):
        with self.assertRaises(ValueError):
            get_user_model().obj.create_user(email=None, password='aasdf')

    def test_create_newSuperUser(self):
        """test if a new super user is created and saved"""
        user = get_user_model().obj.create_superuser(email=default_email,
                                                     password=default_pass)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tah_str(self):
        """Tests the tag string representation"""
        tag = models.Tag.objects.create(user=sample_user(),
                                        name="veg")

        self.assertEqual(str(tag), tag.name)
