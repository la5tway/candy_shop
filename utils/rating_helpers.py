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
    times_len = len(times)
    if times_len:
        return sum(times) / times_len


def calc_rating(courier):
    times = []
    orders = courier.orders.filter(is_delivered=True)
    for region in courier.regions:
        orders_in_regions = orders.filter(region=region).order_by('time_of_delivered')
        avg_dt_in_region = avg_delivery_time_in_region(orders_in_regions)
        if avg_dt_in_region:
            times.append(avg_dt_in_region)
    if len(times):
        return round((60*60 - min(min(times), 60*60)) / (60*60) * 5, 2)
    return 0
