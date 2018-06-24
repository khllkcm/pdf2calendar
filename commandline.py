import os


class CommandLine:
    def __init__(self):
        pass

    def convert(self, args):
        pages = {"A": 0, "B": 1, "C": 2, "D": 3}
        os.system(f"convert -density 300 {args.file}.pdf[{pages[args.group]}] {args.file}.jpg")
        return args.file + ".jpg"

    def delete(self, image):
        os.system(f"rm {image}")
