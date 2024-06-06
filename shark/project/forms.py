from django import forms

from .models import TaskTimeEntry


class DailyReportEntryForm(forms.ModelForm):
    class Meta:
        model = TaskTimeEntry
        fields = ["task", "description", "duration"]


class DailyReportDateForm(forms.Form):
    date = forms.DateField(widget=forms.widgets.DateInput(attrs={"type": "date"}))
