from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Tests the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login in required for retriving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Tests the authorized tags API"""

    def setUp(self):
        self.user = get_user_model().obj.create_user(
            'email@fulltummy.com', 'pass123456')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Tests retriving tags"""
        Tag.objects.create(user=self.user, name="veg")
        Tag.objects.create(user=self.user, name="non-veg")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Tests the tags are listed only for authenticated user"""
        user2 = get_user_model().obj.create_user("useremail2@fulltummy.com",
                                                 "password123457")
        Tag.objects.create(user=user2, name="Gluton-free")
        tag = Tag.objects.create(user=self.user, name="Carbs")

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
