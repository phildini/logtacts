from channels.routing import route

channel_routing = {
    'send-invite': "invitations.consumers.send_invite",
    'process-stripe-webhook': "payments.consumers.process_webhook",
    'process-incoming-email': "contacts.consumers.process_incoming_email",
    'process-vcard-upload': "contacts.consumers.process_vcard_upload",
}