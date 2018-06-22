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


def parse_date(date, start=True):
    if start:
        while date.weekday() != 0:
            date += datetime.timedelta(1)
    else:
        while date.weekday() != 5:
            date -= datetime.timedelta(1)
    return date


def next_date(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    date += datetime.timedelta(1)
    return date


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="PDF full path",
        required=False,
        default="/home/dude/calendar/emploi.pdf",
    )
    parser.add_argument("-g", "--group", help="A,B,C,D", type=str, required=False, default="A")
    parser.add_argument(
        "-s", "--start", help="Start date", type=str, required=False, default="16/06/2018"
    )
    parser.add_argument(
        "-e", "--end", help="End date", type=str, required=False, default="30/07/2018"
    )
    args = parser.parse_args()
    file = args.file
    group = args.group
    start = datetime.datetime.strptime(args.start, "%d/%m/%Y").date()
    end = datetime.datetime.strptime(args.end, "%d/%m/%Y")
    return file, group, start, end


def convert(file, group):
    pages = {"A": 0, "B": 1, "C": 2, "D": 3}
    os.system("convert -density 300 %s[%d] %s.jpg" % (file, pages[group], file[:-4]))
    return file[:-4] + ".jpg"


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
        cv2.imwrite(".temp.png", cell)
        im = Image.open(".temp.png")
        text = pytesseract.image_to_string(im, lang="essai")
        os.system("rm .temp.png")
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
    periods = []
    for j, v in enumerate(vertical[:-1]):
        if j > 0:
            period = []
            for i, h in enumerate(horizontal):
                if i < len(horizontal) - 1 and j < len(vertical) - 1:
                    width = horizontal[i + 1][1] - h[1]
                    height = vertical[j + 1][0] - v[0]
                if i < len(horizontal) - 1 and i not in [0, 4]:
                    cell = img[h[1] + 5 : h[1] + width - 5, v[0] + 5 : v[0] + height - 5]
                    quadrant = cell[0:15, cell.shape[1] - 15 : cell.shape[1]]
                    if np.mean(quadrant) < 240:
                        cv2.line(cell, (cell.shape[1], 5), (3, cell.shape[0]), (255, 255, 255), 5)
                    period.append(extract_text(cell))
            periods.append(period)
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


def process(file, group):
    print("converting file")
    image = convert(file, group)
    print("magic is happenning")
    c = hough_transform_p(image)
    os.system("rm %s" %image)
    return c


def add_date(c, start_date, end_date):
    start = ["%sT08:30:00", "%sT10:10:00", "%sT11:50:00", "%sT14:20:00", "%sT16:00:00"]
    end = ["%sT10:00:00", "%sT11:40:00", "%sT13:20:00", "%sT15:50:00", "%sT17:30:00"]
    for i in range(6):
        for j in range(5):
            if c[i][j].count("*") > 1:
                s1, s2 = c[i][j].replace("\n", " ").replace("  ", " ").replace("|", "l").split(") ")
                c[i][j] = fromstring(s1 + ")")
                if c[i][j]:
                    rule = str(rrule(freq=WEEKLY, interval=2, until=end_date)).split("\n")[1] + "Z"
                c[i][j].extend(
                    (
                        {"dateTime": start[j] % start_date, "timeZone": "Africa/Tunis"},
                        {"dateTime": end[j] % start_date, "timeZone": "Africa/Tunis"},
                        [rule],
                    )
                )
                b = fromstring(s2)
                if b:
                    rule = str(rrule(freq=WEEKLY, interval=2, until=end_date)).split("\n")[1] + "Z"
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
                            str(rrule(freq=WEEKLY, interval=2, until=end_date)).split("\n")[1] + "Z"
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

    pdffile, group, start, end = get_args()
    start = parse_date(start)
    end = parse_date(end, False) + datetime.timedelta(1)
    classes = process(pdffile, group)
    print("parsing")
    events = []
    classes = add_date(classes, start, end)
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
        print("Added %d/%d" % (i + 1, len(events)))
