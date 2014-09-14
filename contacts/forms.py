from django import forms
from django.core.exceptions import ValidationError

from contacts.models import Contact, LogEntry, Tag

class BootstrapForm(object):

    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ContactForm(BootstrapForm, forms.ModelForm):

    class Meta:
        model = Contact


class LogEntryForm(BootstrapForm, forms.ModelForm):

    class Meta:
        model = LogEntry
        fields = ['kind','link','notes']
 

class TagForm(BootstrapForm, forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['tag', 'color']

    def clean(self):

        if self.cleaned_data.get('color') and len(self.cleaned_data.get('color')) > 6:
            raise ValidationError("Hex colors must be six digits or less!")

        return self.cleaned_data

