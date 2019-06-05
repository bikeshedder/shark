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
from shark.utils.fields import AddressField


DocumentStorage = HashedFilenameMetaStorage(storage_class=get_storage_class())


class Document(models.Model):
    title = models.CharField(_('title'),
            max_length=100)
    sender = AddressField(blank=True)
    recipient = AddressField(blank=True)
    vendor = models.ForeignKey('vendor.Vendor',
            verbose_name=_('vendor'),
            on_delete=models.SET_NULL,
            blank=True, null=True)
    customer = models.ForeignKey('customer.Customer',
            verbose_name=_('customer'),
            on_delete=models.SET_NULL,
            blank=True, null=True)
    TYPE_INVOICE = 'invoice'
    TYPE_PAYMENT_REMINDER = 'payment_reminder'
    TYPE_BANK_STATEMENT = 'bank_statement'
    TYPE_QUOTE = 'quote'
    TYPE_MISC = 'misc'
    TYPE_SEPA_DD_MANDATE = 'sepa_dd_mandate'
    TYPE_CHOICES = [
        (TYPE_INVOICE, _('invoice')),
        (TYPE_PAYMENT_REMINDER, _('payment reminder')),
        (TYPE_BANK_STATEMENT, _('bank statement')),
        (TYPE_QUOTE, _('quote')),
        (TYPE_MISC, _('miscellaneous')),
        (TYPE_SEPA_DD_MANDATE, _('SEPA direct debit mandate')),
    ]
    type = models.CharField(_('direction'), max_length=20, choices=TYPE_CHOICES)
    DIRECTION_INTERNAL = 'internal'
    DIRECTION_INBOUND = 'inbound'
    DIRECTION_OUTBOUND = 'outbound'
    DIRECTION_CHOICES = [
        (DIRECTION_INTERNAL, _('internal')),
        (DIRECTION_INBOUND, _('inbound')),
        (DIRECTION_OUTBOUND, _('outbound')),
    ]
    direction = models.CharField(_('direction'), max_length=10, choices=DIRECTION_CHOICES)
    date = models.DateField(_('date'), default=today,
            help_text='Date as written on the document.')
    file = models.FileField(_('file'),
            upload_to='documents', storage=DocumentStorage())
    original_filename = models.TextField(editable=False, blank=True, null=True)
    size = models.BigIntegerField(_('file size'),
            default=0, editable=False)
    mime_type = models.CharField(_('MIME type'),
            blank=True, max_length=100,
            help_text=_('Auto detected from uploaded file'))
    SOURCE_EMAIL = 'email'
    SOURCE_DOWNLOAD = 'download'
    SOURCE_MAIL = 'mail'
    SOURCE_FAX = 'fax'
    SOURCE_RECEIPT = 'receipt'
    SOURCE_SELF = 'self'
    SOURCE_CHOICES = [
        (SOURCE_EMAIL, _('email')),
        (SOURCE_DOWNLOAD, _('download')),
        (SOURCE_MAIL, _('mail')),
        (SOURCE_FAX, _('fax')),
        (SOURCE_RECEIPT, _('receipt')),
        (SOURCE_SELF, _('self')),
    ]
    source = models.CharField(_('original'),
            blank=True,
            max_length=10,
            choices=SOURCE_CHOICES,
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
    instance.original_filename = instance.file.name
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
