from django.contrib import admin
from .models import Invitation
from .forms import InvitationAdminAddForm, InvitationAdminUpdateForm


class InvitationAdmin(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):

        if obj:
            kwargs['form'] = InvitationAdminUpdateForm
        else:
            kwargs['form'] = InvitationAdminAddForm

        return super(InvitationAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Invitation, InvitationAdmin)
