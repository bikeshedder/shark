class IdGenerator(object):
    # This value should be overwritten by subclasses.
    # Typically an invoice number should not exceed 16 characters as a lot
    # of accounting software assumes this limit. 32 chars also allows the
    # use of UUIDs for an ID field which I assume is a sane maximum length.
    max_length = 32

    def __init__(self, model_class=None, field_name=None):
        self.model_class = model_class
        self.model_class_given = model_class is not None
        self.field_name = field_name
        self.field_name_given = field_name is not None

    def get_queryset(self):
        return self.model_class.objects.all().order_by("-%s" % self.field_name)

    def get_last(self) -> str | None:
        obj = self.get_queryset().first()
        return getattr(obj, self.field_name, None)
