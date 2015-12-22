from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from .. import models


class ContactSearchAPIView(APIView):

    permission_classes = (IsAuthenticated,)

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