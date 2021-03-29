from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from utils.api_override import APIOverride as APIView
from utils.orders_helpers import unassigned_orders
from utils.rating_helpers import calc_rating

from .models import Couriers
from .serializers import (
    CourierSerializer, SingleCourierSerializer
)

class CouriersView(APIView):

    def get(self, request):
        data = Couriers.objects.all().order_by("-courier_id")
        if not data.count():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CourierSerializer(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.get('data')
        try:
            serializer = CourierSerializer(data=data, many=True)
            if serializer.is_valid():
                saved_data = serializer.save()
                ids = [{"id": c.courier_id} for c in saved_data]
                return Response({'couriers': ids})
        except ValidationError as exc:
            return Response({"validation_error":{"couriers":exc.detail}}, status=status.HTTP_400_BAD_REQUEST)

class SingleCouriersView(APIView):

    def put(self, request, *args, pk, **kwargs):
        data = request.data
        courier = get_object_or_404(Couriers, pk=pk)
        serializer = CourierSerializer(instance=courier, data=data, partial=True)
        if serializer.is_valid():
            unassigned_orders(courier, data)
            courier = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, pk, **kwargs):
        courier = get_object_or_404(Couriers, pk=pk)
        courier.rating = calc_rating(courier)
        serializer = SingleCourierSerializer(courier)
        return Response(serializer.data)
