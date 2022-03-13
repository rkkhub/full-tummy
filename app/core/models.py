from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """create new user and save"""
        if not email:
            raise ValueError('email address is mandatory')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create new super user and save"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """"Custom user model that supports email than username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    obj = UserManager()
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tags that will be user for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredients to be used in a recepie"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,)

    def __str__(self):
        return self.name
