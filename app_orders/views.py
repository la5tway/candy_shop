from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.api_override import APIOverride as APIView
from utils.mappings import EARNING_MAP, WEIGHT_MAP
from utils.orders_helpers import assigned_orders
from utils.time_helpers import strftime

from .models import Orders, Couriers
from .serializers import OrderSerializer, SingleOrderSerializer


class OrdersView(APIView):
    def get(self, request):
        data = Orders.objects.all()
        if not data.count():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.get('data')
        try:
            serializer = OrderSerializer(data=data, many=True)
            if serializer.is_valid():
                saved_data = serializer.save()
                ids = [{"id": c.order_id} for c in saved_data]
                return Response({'orders': ids})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as exc:
            return Response({"validation_error":{"orders":exc.detail}}, status=status.HTTP_400_BAD_REQUEST)


class SingleOrdersView(RetrieveUpdateDestroyAPIView):
    queryset = Orders.objects.all().prefetch_related("courier")
    serializer_class = SingleOrderSerializer


class OrdersAssign(APIView):
    def post(self, request):

        cid = request.data.get("courier_id")
        courier = get_object_or_404(Couriers, pk=cid)

        orders = Orders.objects.filter(
            region__in=courier.regions,
            weight__lte=WEIGHT_MAP[courier.courier_type],
            courier__isnull=True,
            is_delivered=False,
        )
        if not len(orders):
            return Response({"orders": []})

        assigned, response_orders, working_hours, assign_time = assigned_orders(
            orders, courier.working_hours, courier
        )
        response = dict(orders=response_orders)
        if assigned:
            working_hours = [
                "-".join([strftime(struct_time)
                for struct_time in working_interval])
                for working_interval in working_hours
            ]
            courier.free_working_hours = working_hours
            courier.save()
            response["assign_time"] = assign_time

        return Response(response, status=status.HTTP_200_OK)

class OrderComplete(APIView):

    def post(self, request):
        cid = request.data.get("courier_id")
        oid = request.data.get("order_id")
        courier = Couriers.objects.filter(pk=cid).first()
        order = Orders.objects.filter(pk=oid).first()
        if order.courier != courier:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        complete_time = request.data.get("complete_time")
        order.is_delivered = True
        order.time_of_delivered = complete_time
        order.save()
        courier.earnings += (
            500 * EARNING_MAP[order.courier_type]
        )
        courier.save()
        return Response(
            dict(order_id=oid),
            status=status.HTTP_200_OK
        )
