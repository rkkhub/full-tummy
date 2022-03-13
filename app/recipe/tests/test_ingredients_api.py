from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is reqiored tp access"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test private Ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().obj.create_user(
            email="test_ingredients_user@fulltummy.com",
            password="mypassword"
        )
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient_list(self):
        """Test retriving a list fof ingredients"""
        Ingredient.objects.create(user=self.user, name="Salt")
        Ingredient.objects.create(user=self.user, name="Sugar")

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test if only the ingredients created by user are listed"""
        other_user = get_user_model().obj.create_user(
            email="other_user@fulltummy.com",
            password="mypassword"
        )

        Ingredient.objects.create(user=other_user, name="pepepr")
        ingredient = Ingredient.objects.create(
            user=self.user, name="Green chilli")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
