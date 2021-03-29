import time

def strptime(str_time: str, *, fmt: str = "%H:%M") -> time.struct_time:
    return time.strptime(str_time, fmt)

def strftime(struct_time: time.struct_time, *, fmt: str = "%H:%M") -> str:
    return time.strftime(fmt, struct_time)

def check_intervals(working_hours: list, order_interval: list) -> bool:
    start_order_time, end_order_time = order_interval
    for idx, working_interval in enumerate(working_hours):
        start_wt, end_wt = working_interval
        if start_order_time >= start_wt and end_order_time <=end_wt:
            if start_wt != start_order_time:
                after = [start_wt, start_order_time]
                working_hours.append(after)
            if end_wt != end_order_time:
                before = [end_order_time, end_wt]
                working_hours.append(before)
            working_hours.pop(idx)
            return True
    return False
