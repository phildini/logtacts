from django import forms
from django.core.exceptions import ValidationError
from haystack.forms import ModelSearchForm
from floppyforms import widgets

import contacts as contact_constants
from contacts.models import Contact, ContactField, LogEntry, Tag

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ('name','notes','tags', 'should_surface')
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'rows':3}),
        }

    def __init__(self, *args, **kwargs):
        document_items = None
        self.user = kwargs.pop('user', None)
        if kwargs.get('data'):
            document_items = dict((key, value) for key, value in kwargs.get('data').items() if key.startswith('document'))
        self.book = kwargs.pop('book')
        super(ContactForm, self).__init__(*args, **kwargs)
        choices = Tag.objects.filter(book=self.book).values_list('id', 'tag')
        self.fields['tags'].choices = choices
        self.fields['deleted_fields'] = forms.CharField(required=False)
        if document_items:
            for item in document_items:
                parts = item.split('_')
                field_category = parts[1]
                if len(parts) == 4:
                    if parts[3] == 'pref':
                        self.fields[item] = forms.BooleanField()
                    if parts[3] == 'label':
                        self.fields[item] = forms.CharField(max_length=255)
                else:
                    if field_category == contact_constants.FIELD_TYPE_EMAIL:
                        self.fields[item] = forms.EmailField(max_length=255)
                    if field_category == contact_constants.FIELD_TYPE_URL:
                        self.fields[item] = forms.URLField(max_length=255)
                    if field_category == contact_constants.FIELD_TYPE_DATE:
                        self.fields[item] = forms.DateField()
                    else:
                        self.fields[item] = forms.CharField()

    def clean(self):
        self.has_changed_list = []
        if self.cleaned_data.get('name') != self.instance.name:
            self.has_changed_list.append('Name')
        if self.cleaned_data.get('notes') != self.instance.notes:
            self.has_changed_list.append('Notes')
        if self.cleaned_data.get('should_surface') != self.instance.should_surface:
            self.has_changed_list.append('Send Contact Reminders')
        for field_id in self.cleaned_data.get('deleted_fields', '').split(','):
            if field_id:
                try:
                    ContactField.objects.get(
                        contact=self.instance,
                        id=field_id,
                    ).delete()
                except ContactField.DoesNotExist:
                    pass
        self.instance.book = self.book
        document_items = None
        document_items = dict((key, value) for key, value in self.cleaned_data.items() if key.startswith('document'))
        self.document_field_dicts = {}
        pref_dict = {
            contact_constants.FIELD_TYPE_EMAIL: False,
            contact_constants.FIELD_TYPE_TWITTER: False,
            contact_constants.FIELD_TYPE_URL: False,
            contact_constants.FIELD_TYPE_PHONE: False,
            contact_constants.FIELD_TYPE_ADDRESS: False,
        }
        if document_items:
            for item in document_items:
                parts = item.split('_')
                field_id = parts[2]
                field_type = parts[1]
                field_dict = self.document_field_dicts.get(field_id, {})
                field_dict['type'] = field_type
                if len(parts) == 3:
                    field_dict['value'] = document_items[item]
                if len(parts) == 4:
                    if parts[3] == 'label':
                        field_dict['label'] = document_items[item]
                    if parts[3] == 'pref':
                        if document_items.get(item) and pref_dict.get(field_type):
                            raise ValidationError(
                                'Only one {} can be preferred'.format(field_type),
                            )
                        else:
                            field_dict['pref'] = document_items[item]
                            pref_dict[field_type] = True
                self.document_field_dicts[field_id] = field_dict
        return super(ContactForm, self).clean()

    def save(self, commit=True):        
        response = super(ContactForm, self).save(commit=commit)
        for item in self.document_field_dicts:
            item_dict = self.document_field_dicts[item]
            if item.startswith('new') and item_dict.get('value') and item_dict.get('label'):
                field_object = ContactField.objects.create(
                    kind=item_dict['type'],
                    contact=self.instance,
                    preferred=item_dict.get('pref', False),
                    value = item_dict['value'],
                    label = item_dict['label'],
                )
                field_object.save()
                self.has_changed_list.append(field_object.label)

            else:
                if item_dict['type'] == contact_constants.FIELD_TYPE_DATE:
                    item_dict['value'] = item_dict['value'].strftime('%Y-%m-%d')
                field_object = ContactField.objects.get(
                    id=item,
                    contact=self.instance,
                    kind=item_dict['type'],
                )
                if not (
                    field_object.value == item_dict['value']
                    and field_object.label == item_dict['label']
                    and field_object.preferred == item_dict.get('pref', False)
                ):
                    field_object.value = item_dict['value']
                    field_object.label = item_dict['label']
                    field_object.preferred = item_dict.get('pref', False)
                    self.has_changed_list.append(field_object.label)
                    field_object.save()
        if self.has_changed_list:
            note_str = 'Updated ' + ', '.join(self.has_changed_list)
            LogEntry.objects.create(
                contact = self.instance,
                logged_by = self.user,
                kind = 'edit',
                notes = note_str,
            )

        return response


class LogEntryForm(forms.ModelForm):
    USER_SELECTABLE_CHOICES = (
        ('twitter', 'Twitter'),
        ('tumblr', 'Tumblr'),
        ('facebook', 'Facebook'),
        ('email', 'Email'),
        ('in person', 'In Person'),
        ('website', 'Website'),
        ('other', 'Other'),
    )

    kind = forms.ChoiceField(choices=USER_SELECTABLE_CHOICES)

    class Meta:
        model = LogEntry
        fields = ['kind','link','notes', 'time']
        widgets = {
            'notes': forms.Textarea(attrs={'rows':1}),
            'time': widgets.DateInput(attrs={'class':'form-control'}),
        }
 

class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['tag', 'color']

    def clean(self):

        if self.cleaned_data.get('color') and len(self.cleaned_data.get('color')) > 7:
            raise ValidationError("Hex colors must be six digits or less!")

        if self.cleaned_data.get('color') and not self.cleaned_data.get('color').startswith('#'):
            raise ValidationError("Hex must start with #!")

        return self.cleaned_data


class ContactSearchForm(ModelSearchForm):

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        if self.load_all:
            sqs = sqs.load_all()

        return sqs


class MultiContactForm(forms.Form):

    def __init__(self, *args, **kwargs):
        contact_ids = kwargs.pop('contact_ids')
        super(MultiContactForm, self).__init__(*args, **kwargs)
        for contact_id in contact_ids:
            self.fields['contact_%s' % (contact_id,)] = forms.BooleanField(
                required=False
            )
