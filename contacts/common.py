import json
from .models import Contact

def get_selected_contacts_from_request(request):
    contacts = []
    try:
        selected_contacts = json.loads(
            request.session.get('selected_contacts')
        )
    except TypeError:
        selected_contacts = []
    try:
        contacts = Contact.objects.get_contacts_for_user(
            request.user
        ).filter(
            id__in=selected_contacts
        ).order_by('-created')
    except TypeError:
        pass
    return contacts