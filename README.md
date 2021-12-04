
# pyJapaTalk

-----

JapaTalk is a website that connects people studying Japanese with Japanese teachers.

JapaTalk uses its own calendar system.  This script will export events from JapaTalk's calendar into your Google calendar.

## Setup

Before running, you'll need to download a `credentials.json` file for Google Calendar.  You can find out more information here:

[https://developers.google.com/calendar/quickstart/python](https://developers.google.com/calendar/quickstart/python)

If you update token.json, please delete token.pickle to trigger regeneration of the token file, otherwise an error like
`invalid_grant: Token has been expired or revoked.` will be shown.

## Requirements

webbot will install the latest version of selenium, which it is incompatible with. (should be fixed in the next release)

pip install selenium==3.141.0
pip install google-api-python-client
pip install webbot
pip install pytz
pip install google_auth_oauthlib

## Usage

In order to use this script, first, open `japatalk.py` and navigate to the bottom of the page.  Set `_userName` and `_password`
for your JapaTalk account.

From the terminal type `python japatalk.py`

Some windows will pop up.  Don't touch them or do anything.  Eventually the windows should close and you should see a summary that looks something like:


    Warning: Unmatched events occur for 鈴木先生, 2020-01-14T08:30:00+09:00
    Mom's birthday
    Added the following events:
    ['鈴木先生', '2020-07-04T09:00:00+09:00', '2020-01-14T08:30:00+09:00']

