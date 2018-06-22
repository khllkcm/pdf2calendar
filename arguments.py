import argparse
import datetime


class Arguments:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help="full path to PDF.",
            required=False,
            default="/home/khll/Projects/pdf2calendar/emploi.pdf",
        )
        parser.add_argument(
            "-g", "--group", help="class group: A,B,C,D", type=str, required=False, default="A"
        )
        parser.add_argument(
            "-s",
            "--start",
            help="schedule start date.",
            type=str,
            required=False,
            default="16/06/2018",
        )
        parser.add_argument(
            "-e",
            "--end",
            help="schedule end date.",
            type=str,
            required=False,
            default="30/07/2018",
        )
        args = parser.parse_args()
        self.file = args.file
        self.group = args.group
        self.start = datetime.datetime.strptime(args.start, "%d/%m/%Y").date()
        self.end = datetime.datetime.strptime(args.end, "%d/%m/%Y")
