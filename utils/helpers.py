from IPython.display import display, Markdown
from datetime import datetime


def md(t):
    display(Markdown(t))


def timestamp_to_date(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return str(dt.date())


def seconds_to_hms(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f"{hours:02}:{minutes:02}:{remaining_seconds}"  # Show hour if greater than 0
    else:
        return f"{minutes:02}:{remaining_seconds:02}"


def time_to_seconds(time_str):
    # Check the format of the input string
    if ":" in time_str and len(time_str.split(":")) == 2:  # Format is "M:S"
        t = datetime.strptime(time_str, "%M:%S")
        return t.minute * 60 + t.second
    elif ":" in time_str and len(time_str.split(":")) == 3:  # Format is "H:M:S"
        t = datetime.strptime(time_str, "%H:%M:%S")
        return t.hour * 3600 + t.minute * 60 + t.second
    else:
        raise ValueError(f"Invalid time format: {time_str}")
