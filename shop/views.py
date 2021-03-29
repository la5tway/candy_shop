from typing import Type
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    get_object_or_404,
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView
)
from rest_framework.views import APIView
from .models import Couriers, Orders
from .serializers import (
    CourierSerializer, CourierAllSerializer,
    OrderSerializer, OrderAllSerializer
)
from rest_framework import status
from rest_framework.response import Response
import time
import datetime

WEIGHT_MAP = {
    'foot': 10,
    'bike': 15,
    'car': 50
}
EARNING_KOEF = {
    'foot': 2,
    'bike': 5,
    'car': 9
}

def check(orders, wh, courier = None, assign_time = None):
    assigned = False
    response_orders: list = []
    working_hours: list = [
        [strptime(str_time)
        for str_time in intervals.split("-")]
        for intervals in wh
    ]
    for order in orders:
        for order_intervals in order.delivery_hours:
            order_interval = [
                strptime(str_time)
                for str_time in order_intervals.split("-")
            ]
            if assign_time:
                to_assign = check_intervals(working_hours, order_interval)
                if to_assign:
                    assign_order(response_orders, order, courier, assign_time)
                    assigned = True
            else:
                to_unassign = check_intervals(working_hours, order_interval)
                if not to_unassign:
                    unassign_order(order)
    return assigned, response_orders, working_hours

def unassign_order(order):
    order.courier = None
    order.courier_type = None
    order.save()

def assign_order(response_orders, order, courier, assign_time):
    response_orders.append({"id": order.order_id})
    order.courier = courier
    order.courier_type = courier.courier_type
    order.time_of_assign = assign_time
    order.save()

def assigned_orders(orders, working_hours, courier):
    assign_time: datetime.datetime = datetime.datetime.now()
    check_ = check(
        orders, working_hours, courier, assign_time
    )
    return *check_, assign_time

def unasigned_orders(orders, working_hours):
    check_ = check(orders, working_hours)
    return check_

def strptime(str_time: str, *, fmt: str = "%H:%M") -> time.struct_time:
    return time.strptime(str_time, fmt)

def strftime(struct_time: time.struct_time, *, fmt: str = "%H:%M") -> str:
    return time.strftime(fmt, struct_time)

def check_intervals(working_hours: list, order_interval: list) -> bool:
    start1, end1 = order_interval
    for idx, working_interval in enumerate(working_hours):
        start2, end2 = working_interval
        if start1 >= start2 and end1 <=end2:
            if start2 != start1:
                after = [start2, start1]
                working_hours.append(after)
            if end2 != end1:
                before = [end1, end2]
                working_hours.append(before)
            working_hours.pop(idx)
            return True
    return False
class CouriersView(APIView):
    """Класс курьеров"""
    queryset = Couriers.objects.all()
    serializer_class = CourierSerializer

    def get(self, request):
        data = self.queryset.order_by("-courier_id")
        if data.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.get('data')
        try:
            serializer = self.serializer_class(data=data, many=True)
            if serializer.is_valid():
                saved_data = serializer.save()
                ids = [{"id": c.courier_id} for c in saved_data]
                return Response({'couriers': ids})
        except ValidationError as exc:
            return Response({"validation_error":exc.detail}, status=status.HTTP_400_BAD_REQUEST)

def avg_delivery_time_in_region(orders):
    prev_order = None
    times = []
    for idx, order in enumerate(orders):
        if idx:
            prev_order = orders[idx-1]
        if prev_order:
            prev_time = prev_order.time_of_delivered
        else:
            prev_time = order.time_of_assign
        curr_time = order.time_of_delivered
        times.append((curr_time - prev_time).seconds)
    len_ = len(times)
    if len_:
        return sum(times) / len_


def calc_rating(courier):
    times = []
    orders = courier.orders.filter(is_delivered=True)
    # regions = [int(i) for i in courier.regions.split(",")]
    for region in courier.regions:
        orders_in_regions = orders.filter(region=region).order_by('time_of_delivered')
        avg_dt_in_region = avg_delivery_time_in_region(orders_in_regions)
        if avg_dt_in_region:
            times.append(avg_dt_in_region)
    return (60*60 - min(min(times), 60*60)) / (60*60) * 5


class SingleCouriersView(RetrieveUpdateDestroyAPIView):
    """Класс изменения данных курьера"""
    queryset = Couriers.objects.all()
    serializer_class = CourierSerializer

    def put(self, request, *args, pk, **kwargs):
        data = request.data
        courier = get_object_or_404(self.queryset, pk=pk)
        # serializer = self.get_serializer(request)
        serializer = CourierSerializer(instance=courier, data=data, partial=True)
        if serializer.is_valid():
            _orders = courier.orders.all()
            if "courier_type" in data:
                new_weight = WEIGHT_MAP[data["courier_type"]]
                if new_weight < WEIGHT_MAP[courier.courier_type]:
                    orders = _orders.filter(weight__gte=new_weight)
                    for order in orders:
                        unassign_order(order)
            if "regions" in data:
                # new_regions = set([int(i) for i in data["regions"].split(",")])
                new_regions = set(data["regions"])
                # old_regions = set([int(i) for i in courier.regions.split(",")])
                old_regions = set(courier.regions)
                if len(diff_regions := old_regions - new_regions):
                    orders = _orders.filter(region__in=diff_regions)
                    for order in orders:
                        unassign_order(order)
            if "working_hours" in data:
                new_wh = data["working_hours"]
                unasigned_orders(_orders, new_wh)
            courier = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        courier = self.get_object()
        courier.rating = calc_rating(courier)
        # rating = calc_rating(courier)
        serializer = self.get_serializer(courier)
        # serializer.data["rating"] = calc_rating(courier)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CourierAllSerializer
        return super().get_serializer_class()


class OrdersView(APIView):
    def get(self, request):
        data = Orders.objects.all()
        if data.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
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
            return Response({"validation_error":exc.detail}, status=status.HTTP_400_BAD_REQUEST)

{
    "data": [
        {
            "order_id": 11,
            "weight": 12,
            "region": 1,
            "delivery_hours": ["11:35-14:05"]
        },
        {
            "order_id": 12,
            "weight": 9.99,
            "region": 12,
            "delivery_hours": ["11:35-14:05"]
        },
        {
            "order_id": 13,
            "weight": 0.02,
            "region": 22,
            "delivery_hours": ["11:35-14:05"]
        }
    ]
}

class SingleOrdersView(RetrieveUpdateDestroyAPIView):
    """Класс изменения данных заказа"""
    queryset = Orders.objects.all().prefetch_related("courier")
    serializer_class = OrderAllSerializer



class OrdersAssign(APIView):
    def post(self, request):

        cid = request.data.get("courier_id")
        courier = Couriers.objects.filter(pk=cid).first()
        if not courier:
            return Response(
                {"message": f"курьер с ид {cid} не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # regions = [int(i) for i in courier.regions.split(",")]
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
            500 * EARNING_KOEF[order.courier_type]
        )
        courier.save()
        return Response(
            dict(order_id=oid),
            status=status.HTTP_200_OK
        )


{"courier_id":3}
