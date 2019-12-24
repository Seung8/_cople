from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        user = self.model(email=self.normalize_email(email))

        if password:
            user.set_password(password)

        user.save(**kwargs)

        return user

    def create_superuser(self, email, password):
        super_user = self.create_user(email, password)

        return super_user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='이메일(계정)', max_length=225, unique=True)
    name = models.CharField('이름', max_length=20)
    phone = models.CharField(max_length=30)

    joined_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return '{}({})'.format(self.name, self.email)
