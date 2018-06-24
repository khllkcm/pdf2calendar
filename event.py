import datetime
from utils import *
from dateutil.rrule import *


class Event:
    def __init__(self, cell, start_date, end_date, timezone):

        starts = ["%sT08:30:00", "%sT10:10:00", "%sT11:50:00", "%sT14:20:00", "%sT16:00:00"]
        ends = ["%sT10:00:00", "%sT11:40:00", "%sT13:20:00", "%sT15:50:00", "%sT17:30:00"]
        start = starts[cell.row] % str(start_date + datetime.timedelta(cell.col))
        end = ends[cell.row] % str(start_date + datetime.timedelta(cell.col))
        self.start = {"dateTime": start, "timeZone": timezone}
        self.end = {"dateTime": end, "timeZone": timezone}
        self.summary = parse_summary(cell.text)
        self.description = parse_description(cell.text)
        self.location = parse_location(cell.text)
        self.freq = parse_freq(cell.text, end_date)

    def format(self):
        return {
            "summary": self.summary,
            "description": self.description,
            "location": self.location,
            "start": self.start,
            "end": self.end,
            "recurrence": self.freq,
        }
