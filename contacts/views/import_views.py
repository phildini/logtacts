import boto3
import hashlib
import httplib2
import json
import logging

from allauth.socialaccount.models import SocialToken, SocialApp
from braces.views import LoginRequiredMixin
from channels import Channel
from gargoyle import gargoyle
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.generic import FormView, View

from contacts.forms import UploadForm
from contacts.models import Book

sentry = logging.getLogger('sentry')


class UploadImportView(LoginRequiredMixin, FormView):

    template_name = 'upload_import.html'
    form_class = UploadForm

    def get_success_url(self):
        return reverse('contacts-list', kwargs={'book': self.request.current_book.id})

    def form_invalid(self, form):
        response = super(UploadImportView, self).form_invalid(form)
        return response

    def form_valid(self, form):
        response = super(UploadImportView, self).form_valid(form)
        messages.success(self.request, "We're processing your upload. Your contacts should appear soon!")
        print(form.cleaned_data.get('upload_url'))
        Channel('process-vcard-upload').send({
            'user_id': self.request.user.id,
            'book_id': self.request.current_book.id,
            'url': form.cleaned_data.get('upload_url')
        })
        return response


def sign_s3(request):
    S3_BUCKET = 'contactotter'
    file_name = request.GET.get('file_name')
    file_type = request.GET.get('file_type')

    hashcode = hashlib.sha256(
        bytearray(str(file_name) + str(timezone.now()), 'utf-8'),
    ).hexdigest()[:6]

    file_name = hashcode + file_name

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = file_name,
        Fields = {"acl": "public-read", "Content-Type": file_type},
        Conditions = [
            {"acl": "public-read"},
            {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )

    return JsonResponse({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    })
