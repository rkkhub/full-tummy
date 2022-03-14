from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Ingredient, Recipe

from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='test tag'):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='test ingredient'):
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 2,
        'price': 10.00
    }
    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that auth is required for recipe api"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authorized recipe APIs"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().obj.create_user(
            email="recipe_test@fulltummy.com",
            password="password"
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """"Test getting a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test if only the recipes created by current user are listed"""
        user2 = get_user_model().obj.create_user(
            email="recipe_new_user@fulltummy.com",
            password="password"
        )
        sample_recipe(user=self.user, title="Private recipe")
        sample_recipe(user=user2)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_create(self):
        """Test creating recipe"""
        payload = {
            'title': 'Briyani',
            'time_minutes': 30,
            'price': 10
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_recipe_create_with_tag(self):
        """Test creating a recipe with a tag"""
        tag1 = sample_tag(user=self.user, name='veg')
        tag2 = sample_tag(user=self.user, name='main course')
        payload = {
            'title': 'Paneer Masala',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 10
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_recipe_create_with_ingredients(self):
        """Test create recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='lemon')
        ingredient2 = sample_ingredient(user=self.user, name='sugar')
        payload = {
            'title': 'Lemon juice',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 5,
            'price': 1
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_recipe_patch(self):
        """Test recipe patch api"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='patch tag')
        payload = {
            'title': 'patch title',
            'tags': [new_tag.id]
        }

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_recipe_put(self):
        """Test the full update of a recipe object"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'put title',
            'time_minutes': 20,
            'price': 10.00
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)
