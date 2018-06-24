import numpy as np
import cv2

from cell import Cell


class Table:
    def __init__(self, image):
        def remove_duplicates(lines):
            horizontal, vertical = lines
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

        self.image = cv2.imread(image)
        self.edged_image = self.process_image()
        self.lines = self.extract_lines()
        self.hlines, self.vlines = remove_duplicates(self.sort_lines())

    def process_image(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        median = np.median(blurred)
        lower = int(max(0, (1.7) * median))
        upper = int(min(255, (1.3) * median))
        edged = cv2.Canny(blurred, lower, upper)
        return edged

    def extract_lines(self):
        lines = cv2.HoughLinesP(
            self.edged_image, 1, np.pi / 2, 100, minLineLength=200, maxLineGap=5
        ).tolist()
        return [line[0] for line in lines if line[0][1] > 600]

    def sort_lines(self):
        vertical = [line for line in self.lines if line[0] == line[2]]
        horizontal = [line for line in self.lines if line[1] == line[3]]
        vertical.sort()
        horizontal.sort(key=lambda x: x[1])
        return horizontal, vertical

    def extract_cells(self):
        cells = []
        nc = len(self.vlines[1:-1])
        nl = len(self.hlines[1:-1])
        for j in range(1, nc+1):
            for i in range(1, nl+1):
                if i == 4:
                    continue
                cell = Cell(self.image, self.vlines, j, self.hlines, i)
                if cell.text.count("*") == 2:
                    text_1, text_2 = cell.text.split(") ")
                    cell.text = text_1 + ")"
                    new_cell = Cell(self.image, self.vlines, j, self.hlines, i)
                    new_cell.text = text_2
                    new_cell.col += 7
                    cells.append(new_cell)
                cells.append(cell)
        return cells
