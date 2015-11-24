from django.core.files.storage import get_storage_class
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_hashedfilenamestorage.storage import HashedFilenameMetaStorage
import magic
from taggit.managers import TaggableManager

from shark.utils.date import today


DocumentStorage = HashedFilenameMetaStorage(storage_class=get_storage_class())


class Document(models.Model):
    title = models.CharField(_('title'),
            max_length=100)
    date = models.DateField(_('date'), default=today,
            help_text='Date as written on the document.')
    file = models.FileField(_('file'),
            upload_to='documents', storage=DocumentStorage())
    size = models.BigIntegerField(_('file size'),
            default=0, editable=False)
    mime_type = models.CharField(_('MIME type'),
            blank=True, max_length=100,
            help_text=_('Auto detected from uploaded file'))
    ORIGINAL_EMAIL = 'email'
    ORIGINAL_DOWNLOAD = 'download'
    ORIGINAL_MAIL = 'mail'
    ORIGINAL_FAX = 'fax'
    ORIGINAL_RECEIPT = 'receipt'
    ORIGINAL_CHOICES = [
        (ORIGINAL_EMAIL, _('email')),
        (ORIGINAL_DOWNLOAD, _('download')),
        (ORIGINAL_MAIL, _('mail')),
        (ORIGINAL_FAX, _('fax')),
        (ORIGINAL_RECEIPT, _('receipt')),
    ]
    original = models.CharField(_('original'),
            max_length=10,
            choices=ORIGINAL_CHOICES,
            help_text=u'Where does this document come from?')
    comment = models.TextField(_('comment'),
            blank=True)
    tags = TaggableManager(_('tags'),
            blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    received = models.DateField(_('received'), default=today,
            help_text='Date when the document was received.')

    def __unicode__(self):
        return self.title

@receiver(signals.pre_save, sender=Document)
def document_pre_save(instance, **kwargs):
    instance.size = instance.file.size
    instance.mime_type = magic.from_file(instance.file.file, mime=True)
