
import datetime
from html.parser import HTMLParser

from pytz import timezone
from webbot import Browser

import googleCalendar

timezoneStr = 'Asia/Tokyo'
jst = timezone(timezoneStr)

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


def getJapaTalkCalendar(userName, password):
    web = Browser()
    web.go_to('https://www.japatalk.com/login_form.php')
    web.click(id="wID")
    web.type(userName)
    web.click(id="wPasswd")
    web.type(password)
    web.click(classname="btn-next")
    #web.click(classname="from-cal")
    web.go_to('https://www.japatalk.com/reservation_calendar.php')

    return web.get_page_source()


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

        year, month, day = parser.calendarData[0].split("/")[1].split("'")[0].split('-')
        hour, minute = parser.calendarData[3].split(":")
        teacher = parser.calendarData[4]
        date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
        date = jst.localize(date)

        dates.append([date, teacher])
        i = endI

    return dates


def fmtTime(time):
    return time.isoformat()


def sendDatesToGoogleCalendar(dates):


    service = googleCalendar.loadService()
    thirtyMinutes = datetime.timedelta(seconds=1800)
    oneDay = datetime.timedelta(days=1)

    addedEvents = []
    notAddedEvents = []
    for startTime, teacher in dates:
        endTime = startTime + thirtyMinutes
        yesterday = startTime - oneDay
        reminderDate = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 21, 0, 0)
        reminderDate = jst.localize(reminderDate)
        timeDiff = startTime - reminderDate


        startTimeStr = fmtTime(startTime)
        endTimeStr = fmtTime(endTime)
        alertMinutesBefore = timeDiff.seconds / 60.0

        if googleCalendar.checkIfEventExists(service, startTimeStr, endTimeStr):
            notAddedEvents.append([teacher, startTimeStr, endTimeStr])
        else:
            addedEvents.append([teacher, startTimeStr, endTimeStr])

            startTimeStr = startTimeStr.split('+')
            endTimeStr = endTimeStr.split('+')
            googleCalendar.writeEvent(service, teacher, startTimeStr, endTimeStr, alertMinutesBefore, timezoneStr)

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
