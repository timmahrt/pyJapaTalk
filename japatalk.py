
import os
import datetime
from html.parser import HTMLParser
from copy import deepcopy
import io

from pytz import timezone
from webbot import Browser

import googleCalendar

timezoneStr = 'Asia/Tokyo'
jst = timezone(timezoneStr)

THIRTY_MINUTES = datetime.timedelta(seconds=1800)
ONE_DAY = datetime.timedelta(days=1)

TEACHER = 'teacher'
START = 'start'
STOP = 'stop'

CACHED_FILE_FN = 'cached_calendar.html'

class MyHTMLParser(HTMLParser):

    def __init__(self):
        self.calendarData = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if len(attrs) != 2:
            return

        self.calendarData.append(attrs[1][1])

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        data = data.strip()
        if data != '':
            self.calendarData.append(data)


def getJapaTalkCalendar(userName, password, useCache=False):
    if useCache and os.path.exists(CACHED_FILE_FN):
        with io.open(CACHED_FILE_FN, 'r', encoding="utf-8") as fd:
            pageSource = fd.read()
    else:
        web = Browser()
        web.go_to('https://www.japatalk.com/login_form.php')
        web.click(id="wID")
        web.type(userName)
        web.click(id="wPasswd")
        web.type(password)
        web.click(classname="btn-next")
        #web.click(classname="from-cal")
        web.go_to('https://www.japatalk.com/reservation_calendar.php')
        pageSource = web.get_page_source()

        if useCache:
            with io.open(CACHED_FILE_FN, 'w', encoding="utf-8") as fd:
                fd.write(pageSource)

    return pageSource


def chunkList(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def mergeContinuousEvents(dates):
    returnDates = deepcopy(dates)
    i = 0
    while i + 1 < len(returnDates):
        currentEvent = returnDates[i]
        nextEvent = returnDates[i + 1]
        if currentEvent[TEACHER] == nextEvent[TEACHER] and currentEvent[STOP] == nextEvent[START]:
            currentEvent[STOP] = nextEvent[STOP]
            returnDates.pop(i + 1)
        else:
            i += 1

    return returnDates


def parseJapaTalkCalendarPage(html):
    i = 0
    dates = []
    while True:
        parser = MyHTMLParser()
        try:
            centerI = html.index("koma lesson", i)
        except ValueError:
            break

        startI = html.rindex('<td', i, centerI)
        endI = html.index('</td>', centerI)
        td = html[startI:endI]

        parser.feed(td)
        dateStr = parser.calendarData.pop(0)
        year, month, day = dateStr.split("/")[1].split("'")[0].split('-')
        parser.calendarData.pop(0)  # Unused
        for event in chunkList(parser.calendarData, 3):
            # url = event[0] # Unused
            hour, minute = event[1].split(":")
            teacher = event[2]
            startDate = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
            startDate = jst.localize(startDate)
            endDate = startDate + THIRTY_MINUTES

            dates.append({START: startDate, STOP: endDate, TEACHER: teacher})
        i = endI

    dates = mergeContinuousEvents(dates)

    return dates


def fmtTime(time):
    return time.isoformat()


def sendDatesToGoogleCalendar(dates):
    service = googleCalendar.loadService()

    addedEvents = []
    notAddedEvents = []
    for date in dates:
        startTime = date[START]
        endTime = date[STOP]
        teacher = date[TEACHER]

        yesterday = startTime - ONE_DAY
        reminderDate = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 21, 0, 0)
        reminderDate = jst.localize(reminderDate)
        timeDiff = startTime - reminderDate


        startTimeStr = fmtTime(startTime)
        endTimeStr = fmtTime(endTime)
        alertMinutesBefore = timeDiff.seconds / 60.0

        if googleCalendar.checkIfEventExists(service, teacher, startTimeStr, endTimeStr):
            notAddedEvents.append([teacher, startTimeStr, endTimeStr])
        else:
            addedEvents.append([teacher, startTimeStr, endTimeStr])

            startTimeStr = startTimeStr.split('+')
            endTimeStr = endTimeStr.split('+')
            googleCalendar.writeEvent(
                service,
                teacher,
                startTimeStr,
                endTimeStr,
                alertMinutesBefore,
                timezoneStr)

    if len(addedEvents) == 0:
        print("No new events detected")
    else:
        print("Added the following events:")
        for event in addedEvents:
            print(event)
    if len(notAddedEvents) == 0:
        print("Conflicting or non-existing events:")
        for event in notAddedEvents:
            print(event)


if __name__ == "__main__":
    # Need to specify the userName and password
    html = getJapaTalkCalendar(userName, password)
    dates = parseJapaTalkCalendarPage(html)
    sendDatesToGoogleCalendar(dates)
    _html = getJapaTalkCalendar(_userName, _password, useCache=False)
    _dates = parseJapaTalkCalendarPage(_html)
    sendDatesToGoogleCalendar(_dates)
