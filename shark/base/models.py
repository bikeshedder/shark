from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(
        _("created_at"), auto_now_add=True, editable=False
    )
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True, editable=False)

    class Meta:
        abstract = True


class TaggableMixin(models.Model):
    tags = TaggableManager(_("tags"), blank=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampMixin):
    class Meta:
        abstract = True
