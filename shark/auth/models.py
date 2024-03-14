from django.contrib.auth import models as auth_models
from django.db import models
from django.utils.translation import gettext_lazy as _

from shark.base.models import TimeStampMixin


class UserManager(auth_models.BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        extra_fields = {"is_staff": False, "is_superuser": False, **extra_fields}
        if not email:
            raise ValueError("Users must have an email address")

        user = User(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields = {**extra_fields, "is_staff": True, "is_superuser": True}
        user = self.create_user(email=email, password=password, **extra_fields)
        return user


class User(auth_models.AbstractUser, TimeStampMixin):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "auth_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
