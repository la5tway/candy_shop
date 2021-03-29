import time

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
