from datetime import time


def format_time(value: time) -> str:
    return value.strftime("%H:%M")
