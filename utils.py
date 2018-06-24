import re
from dateutil.rrule import *
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


class Calendar:
    SCOPES = "https://www.googleapis.com/auth/calendar"

    def __init__(self, credentials_file="credentials.json", client_secret="client_secret.json"):
        store = file.Storage(credentials_file)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(client_secret, Calendar.SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build("calendar", "v3", http=creds.authorize(Http()))


def search(regex, string, other_regex=r".*"):
    try:
        result = re.search(regex, string)
        if not result:
            result = re.search(other_regex, string)
        result = result.group()
    except:
        result = ""
    return result


def parse_summary(string):
    regex = [
        r"(^|(?<=\) ))[a-z|A-Z].*?(?= \w\.| [A-Z]\w+(?= (S|s)a| Lab))",
        r"(^[a-z|A-Z]|(?<=\) )).*?(?= [a-z][A-Z].* ((S|s)a|Lab))",
        r"\(.+?\)",
        r"(?<= )\w[A-Z].+?(?= (S|s)a| Lab)",
    ]
    if string:
        summary = search(regex[0], string, regex[1])
        if re.search(r"'\d*$", summary):
            summary = re.sub(r"'\d*$", "*", summary)
        return " ".join([summary, search(regex[2], string, regex[3])])


def parse_location(string):
    regex = r"(?<= )(((S|s)a|Lab)\w* *.*\.*(\d|v|V)).*(?= \()"
    if string:
        location = search(regex, string)
        return location


def parse_description(string):
    regex = r"(?<= )(\w\..+?|[A-Z]\w+)(?= (S|s)a| Lab)"
    if string:
        description = search(regex, string)
        return description


def parse_freq(string, end_date):
    if string.count("*") == 0:
        return [str(rrule(freq=WEEKLY, interval=1, until=end_date)).split("\n")[1] + "Z"]
    elif string.count("*") == 1:
        return [str(rrule(freq=WEEKLY, interval=2, until=end_date)).split("\n")[1] + "Z"]
