from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            name=name
        )

        if password:
            user.set_password(password)

        user.save(**kwargs)

        return user

    def create_superuser(self, email, password, name):
        super_user = self.create_user(email, name, password)
        super_user.is_admin = True
        super_user.is_staff = True
        super_user.is_superuser = True
        super_user.save()

        return super_user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='이메일(계정)', max_length=225, unique=True)
    name = models.CharField('이름', max_length=20)
    phone = models.CharField(max_length=30)

    joined_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return '{}({})'.format(self.name, self.email)

    @property
    def api_keys(self):
        """
        유저 API 정보를 튜플형으로 반환

        return: (액세스키, 시크릿키)
        """
        api_info = UserAPIInfo.objects.filter(user_id=self.pk, is_active=True)

        if not api_info:
            return None
        return api_info.values('access_key', 'secret_key')[0]


class UserAPIInfo(models.Model):
    """API 정보 기록 테이블"""

    user = models.ForeignKey(User, related_name='api_info', on_delete=models.CASCADE)

    access_key = models.CharField(max_length=80)
    secret_key = models.CharField(max_length=80)
    is_active = models.BooleanField('활성', default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'user_api_info'

    def __str__(self):
        return '{}({})'.format(self.user.name, self.user.email)
