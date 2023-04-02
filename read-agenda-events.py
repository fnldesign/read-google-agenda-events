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

import datetime
#from types import NoneType
import httplib2
import pytz
#from datetime import datetime
import os.path
import json
# Imports for Comand Line Args
import getopt, sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/user.emails.read",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/user.addresses.read",
        "openid"]

def get_user_info(credentials):
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    
    user_info = user_info_service.userinfo().get().execute()
    
    people_service = build('people', 'v1', credentials=credentials)
    profile = people_service.people().get(resourceName='people/me', personFields='emailAddresses').execute()



    #connections=people_service.people().connections().list(resourceName='people/me',personFields='names,emailAddresses').execute()
    return user_info

def get_credentials(refresh):
    try:
        if refresh or not os.path.exists('token.json'):
            if  os.path.exists('token.json'):
                os.remove('token.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
             # Save the credentials for the next run
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        else:
            if os.path.exists('token.json'):    
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)        
                

       
    except Exception as e:
        raise Exception("Error in get credential from existing token in disk. Error is: %s" % e)
    
    
    return creds

def parse_date(date, format1, format2):
    date_parsed = None
    try:
        date_parsed = datetime.datetime.strptime(date, format1)
    except ValueError as error1:
        print('Erro in parse data at format [%s]' % format1)
        try:
            date_parsed = datetime.datetime.strptime(date, format2)
        except ValueError as error2:
            print('Erro in parse data at format [%s]' % format2)
    
    return date_parsed

def get_output_file_header():
    #return "start_date;end_date;duration;event\n"
    return "calendar_owner_name;calendar_owner_email;start_date;end_date;duration;event;created;organizaer;attendees[email|name|response_status]\n"

def get_event_attendees(event):
    attendees_string = ''

    if not (event is None and event['attendees'] is None) and len(event['attendees'])>0:
        for attendee in event['attendees']:
            if 'email' in attendee:
                attendees_string = attendees_string + attendee['email'] + '|' 
            else:
                attendees_string = attendees_string + 'None' + '|'


            if 'displayName' in attendee:
                attendees_string = attendees_string + attendee['displayName'] + '|' 
            else:
                attendees_string = attendees_string + 'None' + '|'    

            if 'responseStatus' in attendee:
                attendees_string = attendees_string + attendee['responseStatus'] + '|' 
            else:
                attendees_string = attendees_string + 'None' + '|'

            if 'organizer' in attendee:
                attendees_string = attendees_string + '1|' 
            else:
                attendees_string = attendees_string + '0' + '|'

            if 'self' in attendee:
                attendees_string = attendees_string + '1|' 
            else:
                attendees_string = attendees_string + '0' + '|'

            #Remove last | from string    
            attendees_string=attendees_string[:-1]

            attendees_string=attendees_string + '||'

    #Remove last || from string
    attendees_string=attendees_string[:-2]
    
    return attendees_string

def main():

    format='%Y-%m-%dT%H:%M:%S.00000%Z'
    alternative_format='%Y-%m-%d'
    iso_datetime_format='%Y-%m-%dT%H:%M:%S'

    try:
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        outputEventsData = ""
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if userArguments['refreshToken']:            
            creds = get_credentials(True)
        else:
            creds = get_credentials(False)


        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:            
                creds=get_credentials(True)
            else:
                creds=get_credentials(False)

        #if creds is None:
        #    raise Exception('Error in get credentials')          
        
        
        try:            
            print('Getting Dates for Events')
            try:                

                # Call the Calendar API
                if userArguments["startDate"]=="" or userArguments["endDate"]=="":
                    print("Using Default Dates")
                    #now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                    now_start_day=datetime.datetime.utcnow().strftime('%Y-%m-%dT00:00:00.00000Z')
                    now_end_day = datetime.datetime.utcnow().strftime('%Y-%m-%dT23:59:59.00000Z')
                else:
                    print("Using User Dates")
                    now_start_day=userArguments["startDate"]
                    now_end_day=userArguments["endDate"]         
            except:
                raise Exception("Error in get dates for events")

            print('Getting User Info')
            user_info=get_user_info(creds)
            
            print('Getting the upcoming events')
            try:
                service = build('calendar', 'v3', credentials=creds)
                
                events_result = service.events().list(calendarId='primary', 
                                                    timeMin=now_start_day,
                                                    timeMax=now_end_day,                                               
                                                    singleEvents=True,                                              
                                                    orderBy='startTime').execute()                                              
                events = events_result.get('items', [])
            except Exception as e:
                print('Error in get events in google calendar. Error: %s' % e)
                return   

            if not events:
                print('No upcoming events found.')
                return
            

            #Persist Raw Events in JSON Format
            try:
                #Get Data Interval and User to Put In Raw Data to Classification
                user=user_info['email']
                captured_date=(str(now_start_day))[:10]
                captured_date=datetime.datetime.strptime(captured_date, '%Y-%m-%d')
                month=captured_date.month
                if month < 10:
                    month = '0' + str(month)
                else:
                    month = str(month)
                year=str(captured_date.year)        
                raw_file= "../../fase2-data-exploration/data/raw/google-calendar/{}-{}-{}-events-raw.json".format(user,year,month)

                if  os.path.exists(raw_file):
                    os.remove(raw_file)

                with open(raw_file, 'w+') as f:
                    json.dump(events, f)
            except Exception as e:
                print('Error in persist events to JSON File. Error: %s', e)    
                #Events in JSON is not critical, so if found error program continues

            #TODO> Move this Code to Data Classification
            # Prints the start and name of the next 10 events
            print('Compute Duration of Events')
            duration_total_day=0
            for event in events:
                
                start = event['start'].get('dateTime', event['start'].get('date'))
                if len(start) == 10:
                    start=start + 'T00:00:00-03:00'
                    #start=start + 'T00:00:00.00000'                                    
                start = datetime.datetime.strptime(start[0:19], iso_datetime_format)
                            
                
                end = event['end'].get('dateTime', event['end'].get('date'))
                if len(end) == 10:
                    end=end + 'T23:59:59-03:00'                
                end = datetime.datetime.strptime(end[0:19],iso_datetime_format)

                #print('Getting Event Attendees')
                #try:
                #    attendees_string = get_event_attendees(event)
                #except Exception as error:
                #    print('Error in get event attendees. Error %s' % error)     
                
                duration = end - start
                duration_hours = duration.total_seconds() / 3600
                duration_total_day = duration_total_day + duration_hours
                
                
                if not event is None:
                    if not 'summary' in event:
                        event['summary']=''                 
                    date_time_format="%Y-%m-%d %H:%M:%S"
                    
                    
                    event_data = get_event_data_template()    
                    get_calendar_owner(event_data, user_info)

                    #get_events_details(event_data, event)
                    
                    #get_event_is_internal(event_data, event)

                    #get_event_crm_details(event_data)

                    #get_timesheet_project_details(event_data)
                    
                    #get_solution_activity_type(event_data)

                    #Output 1 - Event Summary
                    # - calendar-owner-email
                    # - calendar-owner-name
                    # - created-datetime
                    # - start-datetime
                    # - end-datetime
                    # - duration                    
                    # - event-organizer-email
                    # - summary
                    # - feauture-event-is-internal or external (include user outside domain @sensedia)
                    # - feature-customer (get from domain outside @sesendia)
                    # - feature-oportunity-stage (get stage from enrichment in HubSopt)
                    # - feature-crm-code (get hubspot code from enrichment in HubSopt)
                    # - feature-crm-oportunity-type (get oportunity-type code from enrichment in HubSopt)
                    # - feature-timesheet-project-code (get jira project code from enrichment in Jira)
                    # - feature-solution-activity-type (identify from IA NLP classify model)
                    #get_event_summary_data(event_data)

                    #Output 2 - Event Details
                    #Events String is composed by
                    # - calendar-owner-email
                    # - calendar-owner-name
                    # - created-datetime
                    # - start-datetime
                    # - end-datetime
                    # - duration
                    # - summary
                    # - description
                    # - event-organizer-email
                    # - attendees-email
                    # - attendees-name
                    # - response-status
                    # - flag-owner-is-organizer
                    # - feauture-event-is-internal or external (include user outside domain @sensedia)
                    # - feature-customer (get from domain outside @sesendia)
                    # - feature-oportunity-stage (get stage from enrichment in HubSopt)
                    # - feature-crm-code (get hubspot code from enrichment in HubSopt)
                    # - feature-crm-oportunity-type (get oportunity-type code from enrichment in HubSopt)
                    # - feature-timesheet-project-code (get jira project code from enrichment in Jira)
                    # - feature-solution-activity-type (identify from IA NLP classify model)
                    #get_event_details_data(event_data)
                    
                    event_string=start.strftime(date_time_format) + ';' + end.strftime(date_time_format) + ";" + str(duration_hours) + ";" + event['summary']
                    outputEventsData += event_string + '\n'
                    print(event_string)            
            
            
            if userArguments['outputFile']!='' and outputEventsData != "":
                with open(userArguments['outputFile'], 'w') as f:
                    f.write(get_output_file_header() + outputEventsData)
                print('Events Data Saved on Outputfile [%s]' % userArguments['outputFile'])    
            print("Total Hours in Meetings:", duration_total_day)

        except Exception as error:
            print('An error occurred: %s' % error)        
    except Exception as error:
        print('An error occurred: %s' % error)

userArguments = {
        "startDate": "",
        "endDate": ""
}

def get_event_data_template():
    event_data_template = {}
    event_data_template['calendar-owner-email']=''
    event_data_template['calendar-owner-name']=''
    event_data_template['created-datetime']=''
    event_data_template['start-datetime']=''
    event_data_template['end-datetime']=''
    event_data_template['duration']=''
    event_data_template['summary']=''
    event_data_template['description']=''
    event_data_template['event-organizer-email']=''
    event_data_template['attendees-sequence-number']=''
    event_data_template['attendees-email']=''
    event_data_template['attendees-name']=''
    event_data_template['attendees-domain']=''
    event_data_template['attendees-is-internal']=''
    event_data_template['attendees-response-status']=''
    event_data_template['flag-owner-is-organizer']=''
    event_data_template['feauture-event-is-internal']=''
    event_data_template['feature-crm-code']=''
    event_data_template['feature-crm-customer']=''
    event_data_template['feature-crm-bizdev']=''
    event_data_template['feature-crm-customer-market']=''
    event_data_template['feature-crm-solution-owner']=''
    event_data_template['feature-crm-oportunity-stage']=''
    event_data_template['feature-crm-oportunity-type']=''
    event_data_template['feature-timesheet-project-code']=''
    event_data_template['feature-solution-activity-type']=''

    return event_data_template

def get_calendar_owner(event_data, user_info):
    if not user_info is None:
        if 'email' in user_info:
            event_data['calendar-owner-email']=user_info['email']
        else:
            event_data['calendar-owner-email']=''

        if 'name' in user_info:    
            event_data['calendar-owner-name']=user_info['name']
    else:
        raise Exception("User Info is None")

def parseCommandLineArguments():
    argumentList = sys.argv[1:] 
    # Options
    options = "hs:e:o:r" 
    # Long options
    long_options = ["help", "start", "end", "outputfile", "refresh"]

    print('Pàrsing CommandLine Args')
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        userArguments["refreshToken"]=False

        # checking each argument
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-h", "--Help"):
                print ("Displaying Help")
                
            elif currentArgument in ("-s", "--start"):
                print (("Displaying Start Date: (% s)") % (currentValue))
                userArguments["startDate"]=currentValue.strip()
                
            elif currentArgument in ("-e", "--end"):
                print (("Displaying End Date: (% s)") % (currentValue))
                userArguments["endDate"]=currentValue.strip()
            elif currentArgument in ("-r", "--refresh"):
                print ('Renew and Refresh Google Auth Token')
                if os.path.exists('token.json'):
                    os.remove('token.json')
                userArguments["refreshToken"]=True
            elif currentArgument in ("-o", "--output"):
                print (("Save Output Event in File: (% s)") % (currentValue))
                outputfile=currentValue.strip()
                if os.path.exists(outputfile):
                    os.remove(outputfile)
                userArguments["outputFile"]=outputfile
    

        now = datetime.datetime.utcnow()
        
        print(userArguments)
        if userArguments["startDate"]=="":
            now_start_day=now.strftime('%Y-%m-%d')
            now_start_day=datetime.datetime.strptime(now_start_day,'%Y-%m-%d')            
            #now_start_day=now_start_day.strftime('%Y-%m-%dT00:00:00.00000Z')
            now_start_day=now_start_day.strftime('%Y-%m-%d')
            
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
        exit

if __name__ == '__main__':
    parseCommandLineArguments()
    main()
