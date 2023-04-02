# Read Events form Google Agenda

This repo was bases on Google Sample App to Get Events with Calendar API https://developers.google.com/calendar/api/quickstart/python

To use it you mest: 
1 - Create an App on Google Developers with minimum scope of read events
2 - Take App Credentials and Put it on file credentials.json, see credentials-sample.json
3 - Use virtualenv o create separation of libs
```
pip3 install virtualenv
virtualenv <your-env>
source <your-env>/bin/activate
```
4 - Execute pip or pip3 install to download dependencies
```
pip3 install -r requirements.txt
```
5 - Run with optional -s ou --start to place start date of events and -e or --end to inform end of events

*** THIS IS AN UNVERIFIED APP, SO GOOGLE CONSENT SCREEN WARN IT.

To solve WARN message, you need follow Google App Verify process, you can see more about this process at https://support.google.com/cloud/answer/7454865

For authorization Google API when you run the read-agenda-events.py Python will open the Google Consent Page, due the Google OAuth Flow require a redirect page I put here together a ngrok util. With ngrok (https://ngrok.com) you able to create an local http proxy on your local machine, exposed to web.

I extend sample to get events, start and end date, compute events hours, sumup its and format in CSV format with comma separator.

I use it to compute my working events to place in a timesheet app.

Use it and feel free to send me feedback by email at fnldesign@gmail.com.