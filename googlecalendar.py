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
