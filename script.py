import numpy as np
import os
import cv2


from googlecalendar import Calendar
from arguments import Arguments
from commandline import CommandLine
from cell import Cell
from event import Event


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
    cells = []
    for j, v in enumerate(vertical[1:-1], 1):
        for i, h in enumerate(horizontal[1:-1], 1):
            if i == 4:
                continue
            cell = Cell(img, vertical, j, horizontal, i)
            if cell.text.count("*") == 2:
                text_1, text_2 = cell.text.split(") ")
                cell.text = text_1 + ")"
                new_cell = Cell(img, vertical, j, horizontal, i)
                new_cell.text = text_2
                new_cell.col += 7
                cells.append(new_cell)
            cells.append(cell)
    return cells


def process(args):
    print("converting file")
    cmd = CommandLine()
    image = cmd.convert(args)
    print("magic is happenning")
    c = hough_transform_p(image)
    cmd.delete(image)
    return c


if __name__ == "__main__":
    calendar = Calendar()
    args = Arguments()
    classes = process(args)
    print("parsing")
    events = [Event(c, args.start, args.end, args.timezone) for c in classes if c.text]
    for i, event in enumerate(events):
        e = calendar.service.events().insert(calendarId="primary", body=event.format()).execute()
        print(f"Added {i+1}/{len(events)}")
