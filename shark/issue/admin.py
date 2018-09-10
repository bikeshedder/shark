from django.contrib import admin

from . import models


class RelationAInline(admin.TabularInline):
    model = models.Relation
    fk_name = 'a'
    extra = 0


class RelationBInline(admin.TabularInline):
    model = models.Relation
    fk_name = 'b'
    extra = 0


class ParticipantInline(admin.TabularInline):
    model = models.Participant
    extra = 0


class NoteInline(admin.StackedInline):
    model = models.Note
    extra = 0


@admin.register(models.Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('project', 'summary', 'created', 'updated')
    list_display_links = ('summary',)
    search_fields = ('project__name', 'summary')
    inlines = (
        RelationAInline,
        RelationBInline,
        ParticipantInline,
        NoteInline,
    )
    ordering = ('-updated',)


class AttachmentInline(admin.StackedInline):
    model = models.Attachment
    extra = 0


class NoteAdmin(admin.ModelAdmin):
    list_display = ('author', 'type', 'text', 'created')
    list_display_links = ('text',)
    search_fields = ('text',)
    ordering = ('-created',)
