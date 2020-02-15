# In accordance with the original license, this work is
# mostly adapted from
# https://developers.google.com/calendar/quickstart/python
# and
# https://developers.google.com/calendar/create-events
from __future__ import print_function

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events',
          ]


def loadService():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def checkIfEventExists(service, startTime, stopTime):
    events_result = service.events().list(calendarId='primary', timeMin=startTime,
                                          timeMax=stopTime,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return len(events) > 0


def writeEvent(service, teacher, startTime, stopTime, reminderMinutes, timeZone):
    event = {
        'summary': teacher + ' skype lesson',
        'start': {
            'dateTime': startTime,
            'timeZone': timeZone,
        },
        'end': {
            'dateTime': stopTime,
            'timeZone': timeZone,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': reminderMinutes},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    service.events().insert(calendarId='primary', body=event).execute()
