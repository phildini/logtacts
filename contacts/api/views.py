from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import renderers as api_renderers
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from .. import models


class ContactSearchAPIView(APIView):

    permission_classes = (IsAuthenticated,)

    def get_renderers(self):
        renderers = [api_renderers.JSONRenderer]
        if self.request.user.is_staff:
            renderers += [api_renderers.BrowsableAPIRenderer]
        return [renderer() for renderer in renderers]


    def get(self, request):
        search_string = request.query_params.get('q')
        if not search_string:
            return Response(
                "No search string",
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            book = models.Book.objects.get(bookowner__user=self.request.user)
        except models.Book.DoesNotExist:
            return Response(
                "No contacts for user",
                status=status.HTTP_400_BAD_REQUEST,
            )
        results = SearchQuerySet().filter(
            book=book.id,
            content=AutoQuery(search_string),
        )
        results = [result.object for result in results]
        serializer = serializers.ContactSerializer(results, many=True)
        return Response(serializer.data)


class TagListCreateAPIView(generics.ListCreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()

    def get_renderers(self):
        renderers = [api_renderers.JSONRenderer]
        if self.request.user.is_staff:
            renderers += [api_renderers.BrowsableAPIRenderer]
        return [renderer() for renderer in renderers]

    def list(self, request):
        queryset = models.Tag.objects.get_tags_for_user(self.request.user)
        serializer = serializers.TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            book = models.Book.objects.get(pk=request.data.get('book')[0])
            bookowner = models.BookOwner.objects.get(book=book, user=request.user)
        except:
            return Response(
                "Not an owner of that book",
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super(TagListCreateAPIView, self).create(request, *args, **kwargs)


class ContactListCreateAPIView(generics.ListCreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ContactSerializer
    queryset = models.Contact.objects.all()

    def get_renderers(self):
        renderers = [api_renderers.JSONRenderer]
        if self.request.user.is_staff:
            renderers += [api_renderers.BrowsableAPIRenderer]
        return [renderer() for renderer in renderers]

    def list(self, request):
        queryset = models.Contact.objects.get_contacts_for_user(
            self.request.user,
        )
        serializer = serializers.ContactSerializer(queryset, many=True)
        return Response (serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            book = models.Book.objects.get(pk=request.data.get('book')[0])
            bookowner = models.BookOwner.objects.get(
                book=book, user=request.user,
            )
        except:
            return Response(
                "Not a valid book",
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super(ContactListCreateAPIView, self).create(
            request, *args, **kwargs
        )
