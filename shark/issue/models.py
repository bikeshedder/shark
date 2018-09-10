from django.db import models
from django.utils.translation import ugettext_lazy as _


class Issue(models.Model):
    project = models.ForeignKey('project.Project', verbose_name=_('project'), on_delete=models.CASCADE)
    summary = models.CharField(_('summary'), max_length=200,
            help_text=_('A concise description of the problem limited to 200 characters.'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    class Meta:
        verbose_name = _('issue')
        verbose_name_plural = _('issues')

    def __str__(self):
        return '[%s] %s' % (self.project, self.summary)


class Relation(models.Model):
    a = models.ForeignKey('issue.Issue', related_name='related_b_set', on_delete=models.CASCADE)
    b = models.ForeignKey('issue.Issue', related_name='related_a_set', on_delete=models.CASCADE)
    b_is_parent = models.BooleanField()
    b_is_related = models.BooleanField()
    b_is_duplicate = models.BooleanField()
    TYPE_PARENT = 'parent'
    TYPE_RELATED = 'related'
    TYPE_DUPLICATE = 'duplicate'
    TYPE_CHOICES = (
        # a has a parent b
        (TYPE_PARENT, _('parent')),
        # a has a related issue b
        (TYPE_RELATED, _('related')),
        # a has a duplicate b
        (TYPE_DUPLICATE, _('duplicate')),
    )
    type = models.CharField(_('type'), max_length=10, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = _('relation')
        verbose_name_plural = _('relations')
        unique_together = (('a', 'b'),)


class Participant(models.Model):
    issue = models.ForeignKey('issue.Issue', verbose_name=_('issue'), on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', verbose_name=_('user'), on_delete=models.CASCADE)
    group = models.ForeignKey('auth.Group', verbose_name=_('group'), on_delete=models.CASCADE)
    watcher = models.BooleanField(default=False)
    reporter = models.BooleanField(default=False)
    waiting = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('participant')
        verbose_name_plural = _('participants')
        unique_together = (('issue', 'user'), ('issue', 'group'))


class Note(models.Model):
    issue = models.ForeignKey('issue.Issue', verbose_name=_('note'), on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', verbose_name=_('author'), on_delete=models.CASCADE)
    TYPE_QUESTION = 'question'
    TYPE_BUG = 'question'
    TYPE_TODO = 'todo'
    TYPE_FEATURE = 'feature'
    TYPE_CHOICES = (
        (TYPE_QUESTION, _('question')),
        (TYPE_BUG, _('bug')),
        (TYPE_FEATURE, _('feature')),
        (TYPE_TODO, _('feature')),
    )
    type = models.CharField(_('type'), max_length=10)
    text = models.TextField()
    created = models.DateTimeField(_('created'), auto_now_add=True)


class Attachment(models.Model):
    note = models.ForeignKey('issue.Note', verbose_name=_('note'), on_delete=models.CASCADE)
    file = models.FileField(_('file'), upload_to='issue/attachment')
    description = models.TextField(_('description'), blank=True)
