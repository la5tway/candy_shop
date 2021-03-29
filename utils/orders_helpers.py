import datetime

from .time_helpers import strptime, check_intervals
from .mappings import WEIGHT_MAP

def _unassigned_orders_in_time(orders, wh, courier = None, assign_time = None):
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
    unasigned_orders_in_time = _unassigned_orders_in_time(
        orders, working_hours, courier, assign_time
    )
    return *unasigned_orders_in_time, assign_time

def unassigned_orders(courier, data):
    _orders = courier.orders.filter(is_delivered=False)
    if "courier_type" in data:
        new_weight = WEIGHT_MAP[data["courier_type"]]
        if new_weight < WEIGHT_MAP[courier.courier_type]:
            orders = _orders.filter(weight__gte=new_weight)
            for order in orders:
                unassign_order(order)
    if "regions" in data:
        new_regions = set(data["regions"])
        old_regions = set(courier.regions)
        if len(diff_regions := old_regions - new_regions):
            orders = _orders.filter(region__in=diff_regions)
            for order in orders:
                unassign_order(order)
    if "working_hours" in data:
        new_wh = data["working_hours"]
        _unassigned_orders_in_time(_orders, new_wh)
