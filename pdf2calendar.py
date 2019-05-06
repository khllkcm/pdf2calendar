from cmd import CommandLine, Arguments
from table import Table
from event import Event
from utils import Calendar

if __name__ == "__main__":
    args = Arguments()
    cmd = CommandLine()
    print(f"Converting {args.file.split('/')[-1]}...")
    image = cmd.convert(args.file, args.group)
    table = Table(image)
    cmd.delete(image)
    print("Extracting cells from table...")
    cells = table.extract_cells()
    print("Parsing cells...")
    events = [Event(cell, args.start, args.end, args.timezone, args.ramadan) for cell in cells if cell.text]
    print("Inserting events into Google Calendar...")
    calendar = Calendar()
    for i, event in enumerate(events):
        e = calendar.service.events().insert(calendarId="primary", body=event.format()).execute()
        print(f"Added {i+1}/{len(events)} events.")
