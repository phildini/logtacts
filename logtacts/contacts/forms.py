from django import forms

from contacts.models import Contact, LogEntry, Tag

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact


class LogEntryForm(forms.ModelForm):

    class Meta:
        model = LogEntry
        fields = ['kind','link','time','notes']
 

class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['tag', 'color']

