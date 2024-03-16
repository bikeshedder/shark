import math
from decimal import Decimal

from shark.utils.rounding import round_to_centi


def decimal_hours_to_time(decimal_hours: Decimal) -> str:
    """
    Converts a Decimal to HH:MM representation
    """
    hours = math.floor(decimal_hours)
    decimal_minutes = decimal_hours % 1 * 60
    minutes = round(decimal_minutes)
    if minutes == 60:
        hours += 1
        minutes = 0
    return f"{hours:02}:{minutes:02}"


def time_to_decimal_hours(time: str) -> Decimal:
    """
    Converts a time in HH:MM representation to hours as a Decimal
    """
    hours, minutes = map(int, time.split(":"))
    decimal_hours = Decimal(hours)
    decimal_minutes = round_to_centi(Decimal(minutes / 60))
    return decimal_hours + decimal_minutes
