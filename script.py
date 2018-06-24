from arguments import Arguments
from commandline import CommandLine
from table import Table
from event import Event
from googlecalendar import Calendar

if __name__ == "__main__":
    args = Arguments()
    cmd = CommandLine()
    print("converting file")
    image = cmd.convert(args.file, args.group)
    print("magic is happenning")
    table = Table(image)
    cmd.delete(image)
    cells = table.extract_cells()
    print("parsing")
    events = [Event(cell, args.start, args.end, args.timezone) for cell in cells if cell.text]
    calendar = Calendar()
    for i, event in enumerate(events):
        e = calendar.service.events().insert(calendarId="primary", body=event.format()).execute()
        print(f"Added {i+1}/{len(events)}")
