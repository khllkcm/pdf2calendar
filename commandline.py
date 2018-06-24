import os


class CommandLine:
    def __init__(self):
        pass

    def convert(self, file, group):
        pages = {"A": 0, "B": 1, "C": 2, "D": 3}
        os.system(f"convert -density 300 {file}.pdf[{pages[group]}] {file}.jpg")
        return file + ".jpg"

    def delete(self, file):
        os.system(f"rm {file}")
