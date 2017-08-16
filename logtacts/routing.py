from channels.routing import route

channel_routing = {
    'send-invite': "invitations.consumers.send_invite",
    'process-stripe-webhook': "payments.consumers.process_webhook",
    'import-google-contacts': "contacts.consumers.import_google_contacts",
    'process-incoming-email': "contacts.consumers.process_incoming_email",
    'process-vcard-upload': "contacts.consumers.process_vcard_upload",
}