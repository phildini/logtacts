from channels.routing import route

channel_routing = {
    'send-invite': "invitations.consumers.send_invite"
}