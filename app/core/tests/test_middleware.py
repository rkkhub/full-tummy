from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

ME_URL = reverse("user:me")
RECIPE_URL = reverse("recipe:recipe-list")


def recipe_detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


class MiddlewareResposeTests(TestCase):
    """Test the custom middleware"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().obj.create_user(
            email="testuser@fulltummy.com",
            password="mypassword")
        self.client.force_authenticate(self.user)

    @override_settings(MAINTENANCE_MODE=True)
    def test_maintenance_mode_on(self):
        """Test maintenance mode enabled response for all methods"""
        payload = {
            'title': 'middleware recipe',
            'price': 10.00,
            'time_minutes': 10,
        }
        recipe = Recipe.objects.create(user=self.user,
                                       title='middleware recipe',
                                       price=10.00,
                                       time_minutes=5,)

        # Test POST
        res_post = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res_post.status_code,
                         status.HTTP_503_SERVICE_UNAVAILABLE)

        # Test GET
        res_get = self.client.get(RECIPE_URL)
        self.assertEqual(res_get.status_code,
                         status.HTTP_503_SERVICE_UNAVAILABLE)

        updated_payload = {
            'title': 'put title',
            'price': 5.00,
            'time_minutes': 10,
        }

        # Test PUT
        res_put = self.client.put(
            recipe_detail_url(recipe.id), updated_payload)
        self.assertEqual(res_put.status_code,
                         status.HTTP_503_SERVICE_UNAVAILABLE)

        # Test PATCH
        res_patch = self.client.patch(
            recipe_detail_url(recipe.id), updated_payload)
        self.assertEqual(res_patch.status_code,
                         status.HTTP_503_SERVICE_UNAVAILABLE)

    @override_settings(MAINTENANCE_MODE=False)
    def test_maintenance_mode_off(self):
        """Test maintenance mode disabled response"""
        payload = {
            'title': 'middleware recipe',
            'price': 10.00,
            'time_minutes': 10,
        }
        recipe = Recipe.objects.create(user=self.user,
                                       title='middleware recipe',
                                       price=10.00,
                                       time_minutes=5,)

        # Test POST
        res_post = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res_post.status_code, status.HTTP_201_CREATED)

        # Test GET
        res_get = self.client.get(RECIPE_URL)
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)

        updated_payload = {
            'title': 'put title',
            'price': 5.00,
            'time_minutes': 10,
        }

        # Test PUT
        res_put = self.client.put(
            recipe_detail_url(recipe.id), updated_payload)
        self.assertEqual(res_put.status_code, status.HTTP_200_OK)

        # Test PATCH
        res_patch = self.client.patch(
            recipe_detail_url(recipe.id), updated_payload)
        self.assertEqual(res_patch.status_code,
                         status.HTTP_200_OK)
