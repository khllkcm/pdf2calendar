import numpy as np
import os
import cv2
from PIL import Image
import pytesseract
import argparse
import re
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
from dateutil.rrule import *


from googlecalendar import Calendar
from arguments import Arguments
from commandline import CommandLine


def next_date(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    date += datetime.timedelta(1)
    return date


def remove_duplicates(horizontal, vertical):
    for k in range(5):
        i, j = 0, 0
        while i < len(horizontal[:-1]):
            diff = abs(horizontal[i][1] - horizontal[i + 1][1])
            if diff < 5:
                del horizontal[i + 1]
            i = i + 1
        while j < len(vertical[:-1]):
            diff = abs(vertical[j][0] - vertical[j + 1][0])
            if diff < 5:
                del vertical[j + 1]
            j = j + 1
    return horizontal, vertical


def sort_line_list(lines):
    vertical = [line for line in lines if line[0] == line[2]]
    horizontal = [line for line in lines if line[1] == line[3]]
    vertical.sort()
    horizontal.sort(key=lambda x: x[1])
    return horizontal, vertical


def auto_canny(image, sigma=0.3):
    v = np.median(image)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    return edged


def extract_text(cell):
    if cell.any():
        text = pytesseract.image_to_string(cell, lang="essai")
    return text if len(text) > 2 else ""


def hough_transform_p(image):
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = auto_canny(blurred)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 2, 100, minLineLength=200, maxLineGap=5).tolist()
    lines = [line[0] for line in lines]
    lines = [line for line in lines if line[1] > 600]
    horizontal, vertical = sort_line_list(lines)
    horizontal, vertical = remove_duplicates(horizontal, vertical)
    periods = [[[] for i in range(len(horizontal)-3)] for i in range(len(vertical)-2)]
    for j, v in enumerate(vertical[1:-1],1):
        width = vertical[j+1][0] - vertical[j][0]
        for i, h in enumerate(horizontal[1:-1],1):
            if i ==4:
                continue
            height = horizontal[i+1][1] - horizontal[i][1]
            pos_x = v[0]; pos_y=h[1]
            cell = img[pos_y + 5 : pos_y + height - 5, pos_x + 5 : pos_x + width - 5]
            quadrant = cell[0:15, cell.shape[1] - 15 : cell.shape[1]]
            if np.mean(quadrant) < 240:
                cv2.line(cell, (cell.shape[1], 5), (3, cell.shape[0]), (255, 255, 255), 5)
            periods[j-1][max(i-1,i%4)-1] = extract_text(cell)
    return periods


def search(regex, string, other_regex=r".*"):
    try:
        result = re.search(regex, string)
        if not result:
            result = re.search(other_regex, string)
        result = result.group()
    except:
        result = ""
    return result


def fromstring(string):
    regex = [
        r"(^|(?<=\) ))[a-z|A-Z].*?(?= \w\.| [A-Z]\w+(?= (S|s)a| Lab))",
        r"(?<= )(\w\..+?|[A-Z]\w+)(?= (S|s)a| Lab)",
        r"\(.+?\)",
        r"(?<= )(((S|s)a|Lab)\w* *.*\.*(\d|v|V)).*(?= \()",
        r"(^[a-z|A-Z]|(?<=\) )).*?(?= [a-z][A-Z].* ((S|s)a|Lab))",
        r"(?<= )\w[A-Z].+?(?= (S|s)a| Lab)",
    ]
    if string:
        string = string.replace("\n", " ").replace("  ", " ").replace("|", "l")
        summary = search(regex[0], string, regex[4])
        if re.search(r"'\d*$", summary):
            summary = re.sub(r"'\d*$", "*", summary)
        classtype = " " + search(regex[2], string, regex[5])
        summary += classtype
        description = search(regex[1], string)
        location = search(regex[3], string)
        return [summary, description, location]


def process(args):
    print("converting file")
    cmd = CommandLine()
    image = cmd.convert(args)
    print("magic is happenning")
    c = hough_transform_p(image)
    os.system(f"rm {image}")
    return c


def add_date(c, start_date, end_date):
    start = ["%sT08:30:00", "%sT10:10:00", "%sT11:50:00", "%sT14:20:00", "%sT16:00:00"]
    end = ["%sT10:00:00", "%sT11:40:00", "%sT13:20:00", "%sT15:50:00", "%sT17:30:00"]
    for i in range(6):
        for j in range(5):
            if c[i][j].count("*") > 1:
                s1, s2 = (
                    c[i][j].replace("\n", " ").replace("  ", " ").replace("|", "l").split(") ")
                )
                c[i][j] = fromstring(s1 + ")")
                if c[i][j]:
                    rule = (
                        str(rrule(freq=WEEKLY, interval=2, until=end_date)).split("\n")[1] + "Z"
                    )
                c[i][j].extend(
                    (
                        {"dateTime": start[j] % start_date, "timeZone": "Africa/Tunis"},
                        {"dateTime": end[j] % start_date, "timeZone": "Africa/Tunis"},
                        [rule],
                    )
                )
                b = fromstring(s2)
                if b:
                    rule = (
                        str(rrule(freq=WEEKLY, interval=2, until=end_date)).split("\n")[1] + "Z"
                    )
                b.extend(
                    (
                        {
                            "dateTime": start[j] % (start_date + datetime.timedelta(7)),
                            "timeZone": "Africa/Tunis",
                        },
                        {
                            "dateTime": end[j] % (start_date + datetime.timedelta(7)),
                            "timeZone": "Africa/Tunis",
                        },
                        [rule],
                    )
                )
                c.append([b])
            else:
                c[i][j] = fromstring(c[i][j])
                if c[i][j]:
                    if "*" in c[i][j][0]:
                        rule = (
                            str(rrule(freq=WEEKLY, interval=2, until=end_date)).split("\n")[1]
                            + "Z"
                        )
                    else:
                        rule = str(rrule(freq=WEEKLY, until=end_date)).split("\n")[1] + "Z"
                    c[i][j].extend(
                        (
                            {"dateTime": start[j] % start_date, "timeZone": "Africa/Tunis"},
                            {"dateTime": end[j] % start_date, "timeZone": "Africa/Tunis"},
                            [rule],
                        )
                    )
        start_date = next_date(str(start_date))
    return c


if __name__ == "__main__":
    calendar = Calendar()
    args = Arguments()
    classes = process(args)
    print("parsing")
    events = []
    classes = add_date(classes, args.start, args.end)
    for day in classes:
        for period in day:
            if period:
                events.append(
                    dict(
                        zip(
                            ["summary", "description", "location", "start", "end", "recurrence"],
                            period,
                        )
                    )
                )
    for i, event in enumerate(events):
        e = calendar.service.events().insert(calendarId="primary", body=event).execute()
        print(f"Added {i+1}/{len(events)}")
