from django import forms

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

