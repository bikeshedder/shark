from os.path import basename, splitext
from tempfile import TemporaryFile

from django.core.files.storage import get_storage_class
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_hashedfilenamestorage.storage import HashedFilenameMetaStorage
import magic
from taggit.managers import TaggableManager
from wand.image import Image
from wand.exceptions import MissingDelegateError

from shark.utils.date import today


DocumentStorage = HashedFilenameMetaStorage(storage_class=get_storage_class())


class Document(models.Model):
    title = models.CharField(_('title'),
            max_length=100)
    # XXX sender
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
            blank=True,
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

    THUMBNAIL_FIELDS = (
        ('thumbnail_small', 'sm', '128x128'),
        ('thumbnail_medium', 'md', '256x256'),
        ('thumbnail_large', 'lg', '512x512'),
    )
    thumbnail_small = models.ImageField(upload_to='documents',
            editable=False)
    thumbnail_medium = models.ImageField(upload_to='documents',
            editable=False)
    thumbnail_large = models.ImageField(upload_to='documents',
            editable=False)

    def __str__(self):
        return self.title

def create_thumbnails(doc):
    # create thumbnails
    fn, ext = splitext(basename(doc.file.name))
    fh = doc.file.open()
    try:
        with Image(file=fh) as orig:
            if len(orig.sequence) == 0:
                clear_thumbnails(doc)
            with Image(orig.sequence[0]) as thumb:
                thumb.format = 'png'
                for field_name, suffix, size in Document.THUMBNAIL_FIELDS:
                    thumb_clone = thumb.clone()
                    thumb_clone.transform('', size)
                    with TemporaryFile() as tmp:
                        thumb_clone.save(file=tmp)
                        tmp.seek(0)
                        field = getattr(doc, field_name)
                        field.save(f'{fn}_{suffix}.png', tmp, save=False)
    except MissingDelegateError:
        clear_thumbnails(doc)

def clear_thumbnails(doc):
    changed = False
    for field_name, suffix, size in Document.THUMBNAIL_FIELDS:
        field = getattr(doc, field_name)
        if field:
            getattr(doc, field_name).delete()
        changed = True
    return changed

@receiver(signals.pre_save, sender=Document)
def document_pre_save(instance, raw, **kwargs):
    if raw:
        return
    instance.size = instance.file.size
    instance.mime_type = magic.from_buffer(instance.file.read(1024), mime=True)
    instance._file_changed = not instance.pk or \
            Document.objects.get(pk=instance.pk).file != instance.file

@receiver(signals.post_save, sender=Document)
def document_post_save(instance, raw, **kwargs):
    if raw:
        return
    if instance._file_changed:
        create_thumbnails(instance)
        Document.objects.filter(pk=instance.pk).update(**{
            field_name: getattr(instance, field_name)
            for field_name, _unused, _unused in Document.THUMBNAIL_FIELDS
        })
