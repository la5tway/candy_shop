from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

class APIOverride(APIView):
    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return super().handle_exception(exc)
