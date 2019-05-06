import os
import argparse
import datetime


class CommandLine:
    def __init__(self):
        pass

    def convert(self, file, group):
        pages = {"A": 0, "B": 1, "C": 2, "D": 3}
        os.system(f"convert -density 300 {file}.pdf[{pages[group]}] {file}.jpg")
        return file + ".jpg"

    def delete(self, file):
        os.system(f"rm {file}")


class Arguments:
    def __init__(self):
        def parse_date(date, start=True):
            if start:
                while date.weekday() != 0:
                    date += datetime.timedelta(1)
            else:
                while date.weekday() != 6:
                    date -= datetime.timedelta(1)
            return date

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help="Path to PDF.",
            required=True,
            default="input/table.pdf",
        )
        parser.add_argument(
            "-g", "--group", help="class group: A,B,C,D", type=str, required=True, default="A"
        )
        parser.add_argument(
            "-s",
            "--start",
            help="schedule start date.",
            type=str,
            required=True,
            default="16/01/2018",
        )
        parser.add_argument(
            "-e",
            "--end",
            help="schedule end date.",
            type=str,
            required=True,
            default="30/04/2018",
        )
        parser.add_argument(
            "-t", "--timezone", help="Timezone", type=str, required=False, default="Africa/Tunis"
        )

        parser.add_argument(
            "-r", "--ramadan", help="Ramadan", type=lambda x: (str(x).lower() == 'true'), required=False, default=False
        )

        args = parser.parse_args()
        self.file = args.file[:-4]
        self.group = args.group
        self.start = parse_date(datetime.datetime.strptime(args.start, "%d/%m/%Y").date())
        self.end = parse_date(datetime.datetime.strptime(args.end, "%d/%m/%Y"), False)
        self.timezone = args.timezone
        self.ramadan = args.ramadan