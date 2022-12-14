# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START calendar_quickstart]
from __future__ import print_function

import datetime
import httplib2
import pytz
#from datetime import datetime
import os.path

# Imports for Comand Line Args
import getopt, sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials(refresh):
    if refresh or not os.path.exists('token.json'):
        if  os.path.exists('token.json'):
            os.remove('token.json')
        flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    else:
        if os.path.exists('token.json'):    
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)        

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    return creds

def get_output_file_header():
    return "start_date;end_date;duration;event\n"   

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    outputEventsData = ""
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = get_credentials(False)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:            
            creds=get_credentials(True)
        else:
            creds=get_credentials(False)
       
    try:
        service = build('calendar', 'v3', credentials=creds)

        format='%Y-%m-%dT%H:%M:%S%z'

        # Call the Calendar API
        if userArguments["startDate"]=="" or userArguments["endDate"]=="":
            print("Using Default Dates")
            #now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            now_start_day=datetime.datetime.utcnow().strftime('%Y-%m-%dT00:00:00.000000Z')
            now_end_day = datetime.datetime.utcnow().strftime('%Y-%m-%dT23:59:59.000000Z')
        else:
            print("Using User Dates")
            now_start_day=userArguments["startDate"]
            now_end_day=userArguments["endDate"]         
        
        
        print('Getting the upcoming events')
        events_result = service.events().list(calendarId='primary', 
                                              timeMin=now_start_day,
                                              timeMax=now_end_day,                                               
                                              singleEvents=True,                                              
                                              orderBy='startTime').execute()                                              
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        duration_total_day=0
        for event in events:
            
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = datetime.datetime.strptime(start, format)
                        
            end = event['end'].get('dateTime', event['end'].get('date'))
            end = datetime.datetime.strptime(end,format)

            duration = end - start
            duration_hours = duration.total_seconds() / 3600
            duration_total_day = duration_total_day + duration_hours
            
            date_time_format="%Y-%m-%d %H:%M:%S"
            event_string=start.strftime(date_time_format) + ';' + end.strftime(date_time_format) + ";" + str(duration_hours) + ";" + event['summary']
            outputEventsData += event_string + '\n'
            print(event_string)            
        
        if userArguments['outputFile']!='' and outputEventsData != "":
            with open(userArguments['outputFile'], 'w') as f:
                f.write(get_output_file_header() + outputEventsData)
            print('Events Data Saved on Outputfile [%s]' % userArguments['outputFile'])    
        print("Total Hours in Meetings:", duration_total_day)

    except HttpError as error:
        print('An error occurred: %s' % error)



userArguments = {
        "startDate": "",
        "endDate": ""
}

def parseCommandLineArguments():
    argumentList = sys.argv[1:] 
    # Options
    options = "hs:e:o:r" 
    # Long options
    long_options = ["help", "start", "end", "outputfile", "refresh"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        # checking each argument
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-h", "--Help"):
                print ("Displaying Help")
                
            elif currentArgument in ("-s", "--start"):
                print (("Displaying Start Date: (% s)") % (currentValue))
                userArguments["startDate"]=currentValue
                
            elif currentArgument in ("-e", "--end"):
                print (("Displaying End Date: (% s)") % (currentValue))
                userArguments["endDate"]=currentValue
            elif currentArgument in ("-r", "--refresh"):
                print ('Renew and Refresh Google Auth Token')
                if os.path.exists('token.json'):
                    os.remove('token.json')
                userArguments["refreshToken"]=True
            elif currentArgument in ("-o", "--output"):
                print (("Save Output Event in File: (% s)") % (currentValue))
                outputfile=currentValue
                if os.path.exists(outputfile):
                    os.remove(outputfile)
                userArguments["outputFile"]=outputfile
    

        now = datetime.datetime.utcnow()
        
        print(userArguments)
        if userArguments["startDate"]=="":
            now_start_day=now.strftime('%Y-%m-%d')
            now_start_day=datetime.datetime.strptime(now_start_day,'%Y-%m-%d')            
            now_start_day=now_start_day.strftime('%Y-%m-%dT00:00:00.00000Z')
            print("Using Default Start Date as [%s]" % (now_start_day))            
            userArguments["startDate"]=now_start_day            
        else:
            now_start_day=datetime.datetime.strptime(userArguments["startDate"],'%Y-%m-%d')
            now_start_day=now_start_day.strftime('%Y-%m-%dT00:00:00.00000Z')
            print("Using User Start Date as [%s]" % (now_start_day))            
            userArguments["startDate"]=now_start_day            
        
        if userArguments["endDate"]=="":
            now_end_day=userArguments["startDate"]
            now_end_day=datetime.datetime.strptime(now_end_day,'%Y-%m-%dT00:00:00.00000Z')
            now_end_day=now_end_day.strftime('%Y-%m-%dT23:59:59.00000Z')
            print("Using Default End Date as [%s]" % (now_end_day))            
            userArguments["endDate"]=now_end_day
        else:
            now_end_day=datetime.datetime.strptime(userArguments["endDate"],'%Y-%m-%d')
            now_end_day=now_end_day.strftime('%Y-%m-%dT23:59:59.00000Z')
            print("Using User End Date as [%s]" % (now_end_day))
            userArguments["endDate"]=now_end_day

        if not 'outputFile' in userArguments.keys():
            userArguments['outputFile']=''
        
        if not 'refresh' in userArguments.keys():
            userArguments['refresh']=False
            
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

if __name__ == '__main__':
    parseCommandLineArguments()
    main()
# [END calendar_quickstart]