import cv2
import numpy as np
import pytesseract


class Cell:
    def __init__(self, image, vertical, j, horizontal, i):

        self.padding = 5
        self.x = vertical[j][0] + self.padding
        self.y = horizontal[i][1] + self.padding
        self.width = vertical[j + 1][0] - vertical[j][0] - 2 * self.padding
        self.height = horizontal[i + 1][1] - horizontal[i][1] - 2 * self.padding
        self.image = image[self.y : self.y + self.height, self.x : self.x + self.width]
        self.quadrant = self.image[0:15, self.width - 15 : self.width]
        self.text = self.grab_text()
        self.col = j - 1
        self.row = max(i - 1, i % 4) - 1

    def grab_text(self):
        def fix_diag(cell):
            if np.mean(cell.quadrant) < 240:
                cv2.line(cell.image, (cell.width, 5), (3, cell.height), (255, 255, 255), 5)

        if self.image.any():
            fix_diag(self)
            text = pytesseract.image_to_string(self.image, lang="essai")
        if len(text) > 2:
            return text.replace("\n", " ").replace("  ", " ").replace("|", "l")
        else:
            return ""
