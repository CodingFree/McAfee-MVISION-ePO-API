import json
import requests
import logging
import sys
import time
from datetime import datetime, timedelta

import CEFProcessor

##### Based on https://github.com/mohlcyber/McAfee-MVISION-ePO-API

class McAfeeReader():
  """
  Class used to get events from McAfee MVISION API and write them to a file.

  ...

  Attributes
  ----------
  user: str
    User credential to connect MVISON API
  password: str
    Password credential to connect MVISON API
  client_id: str
    Client ID credential to connect MVISON API. Obtained on https://auth.ui.mcafee.com/support.htm
  sleep_seconds: int
    Seconds to sleep between two different requests. (Default: 10)
  base: str
    Region endpoint where MVSION tenant is deployed. It could be configured through
    region paramenter that could be between US, SI, EU and SY. (Default: EU)
  scope: str
    API events request scope. (Default epo.evt.r)
  logger: Logger
    Logger object to store all logs
  auth_url: str
    URL where authorization endpoint is defined. (Default: https://iam.mcafee-cloud.com/iam/v1.0/token)
  session: requests.Session()
    Session where requests are made
  max_log_age_hours: int
    Log file hours retention. (Default: 12).
    
  Methods
  -------
  auth()
    Get authorization headers for client requests through the authorization API (must be executed at least once
    each 24 hours) because token retrieved has 24 hours of validity.
  events(since,until,ev_type)
    Function that request to API for events between the time lapse passed as argument.
  write(evts,prefix,path)
    Function that writes JSON events received to the path and file passed as argument.
  rotate(prefix,path)
    Funcion that deletes old log files based on max_log_age_hours defined in class object
  main()
    Function that handles events requests every X seconds configured and writes events to a file. It also handles
    log file rotation by deleting old files each configured time (using rotate function).
  """
  def __init__(self,user,password,client_id,sleep_seconds=10,region='EU',scope='epo.evt.r',
         logger_name='mcafee',max_log_age_hours=12):
    self.logger = logging.getLogger(logger_name)
    self.logger.setLevel('INFO')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)

    self.auth_url = 'https://iam.mcafee-cloud.com/iam/v1.0/token'
    if region == 'US':
      self.base = 'arevents.mvision.mcafee.com'
    elif region == 'SI':
      self.base = 'areventssgp.mvision.mcafee.com'
    elif region == 'EU':
      self.base = 'areventsfrk.mvision.mcafee.com'
    elif region == 'SY':
      self.base = 'areventssyd.mvision.mcafee.com'

    self.user = user
    self.password = password

    # Login to the MVISION EPO console and open a new tab
    # go to https://auth.ui.mcafee.com/support.html to retrieve your client_id
    self.client_id = client_id
    self.scope = scope

    headers = {'Accept': 'application/json'}

    self.session = requests.Session()
    self.session.headers = headers
    
    self.max_log_age_hours = max_log_age_hours
    self.auth()
    
  def auth(self):
    """
    Retrieves an authorization token from IAM API
    """
    data = {
      "username": self.user,
      "password": self.password,
      "client_id": self.client_id,
      "scope": self.scope,
      "grant_type": "password"
    }

    res = requests.post(self.auth_url, data=data)
    if res.ok:
      token = res.json()['access_token']
      self.session.headers.update({'Authorization': 'Bearer ' + token})
      self.logger.info('Successfully authenticated.')
    else:
      self.logger.error('Could not authenticate. {0} - {1}'.format(str(res.status_code), res.text))
      sys.exit()
  
  def events(self,since,until,ev_type='all'):
    """
    Retrieves events from API using authorization token from class object and returns them as JSON dump
    
    Parameters
    ----------
    since : str
      String containing initial time where events are recollected
    until: str
      String containing end time where events are recollected
    ev_type: str
      Type of events that are recollected. Possible values: threats, incidents or all. (Default: all).
    rest of the class attributes needed.
    """
    params = {
      'type': ev_type,  # threats, incidents (dlp), all
      'since': since,
      'until': until,
      'limit': str(args.limit)
    }

    res = self.session.get('https://{0}/eventservice/api/v2/events'.format(self.base), params=params)

    if res.ok:
      return res.json()
    else:
      self.logger.error('Could not retrieve MVISION EPO Events. {0} - {1}'.format(str(res.status_code),res.text))
      sys.exit()
      
  def write(self,evts,now,prefix='mcafee-events',path='/var/log/mcafee/'):
    """
    Writes events received to a file
    
    Parameters
    ----------
    evts : list
      Events to write
    now: datetime
      Events recollection time to format name
    prefix, path: str
      Logs path and prefix where store log files. Format is: <path>/<prefix>-<mmdd.H>.log.
      (Default: path: /var/log/mcafee/, prefix: mcafee-events)
    """
    timeSlice = now.strftime("%m%d.%H")
    if path[-1] != '/':
      path += '/'
    filename = path + prefix+'-'+timeSlice+'.log'
    with open(filename,'a') as f:
      for event in evts['Events']:
        f.write(json.dumps(event))
        
  def rotate(self,prefix='mcafee-events',path='/var/log/mcafee/'):
    """
    Delete log files older than max_log_age_hours by using ctime (in Linux it would take last modification time)
    
    Parameters
    ----------
    prefix, path: str
      Logs path and prefix where logs are stored. (Default: path: /var/log/mcafee/, prefix: mcafee-events)
    """
    filenames = path + prefix+'-*.json'
    files = glob.glob(filenames)
    now = time.time()
    for file in files:
      f_time = os.stat(file)[8] # ctime
      if (now - f_time)/3600 >= self.max_log_age_hours:
        os.remove(file)
        self.logger.info("Removing file {0} for rotation policy".format(file))

  def main(self):
    now = datetime.utcnow()
    end_hour = (now.hour + 23) % 24 # now.hour - 1 ?
    roatation_hour = (now.hour + max_log_age_hours) % 24
    attribs = {
      "deviceVendor": "McAfee",
      "deviceId": "McAfee EPO",
      "deviceVersion": "SaaS",
      "timeKey": "EventTime",
      "hostKey": "ServerID",
      "severityKey": "ThreatSeverity",
      "typeKey": "SourceModuleName",
      "subTypeKey": "SourceModuleType",
      "signatureIdKey": "AutoID",
    }
    while True:
      delay_begin = time.time()
      # calculates loop requested times (since -> since + sleep time)
      until_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
      since_iso = (now - timedelta(seconds=self.sleep_seconds)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
      # retrieve events and write them to file
      events = self.events(since=since_iso,until=until_iso)
      # convert events to CEF format using CEFProcessor module
      cef_events = CEFProcessor.CEFProcessor(events,attribs).process_events()
      self.write(cef_events,now)
      # if day has finished, recreate token auth and restart end_hour variable
      if now.hour == end_hour:
        self.auth()
        end_hour = (now.hour + 23) % 24
      # check if rotation time has arrived and then checks every hour
      if now.hour == roatation_hour:
        self.rotate()
        roatation_hour = (now.hour + 1) % 2
      # to avoid events loss, uses loop execution time to substract it to wait time
      delay = time.time() - delay_begin
      time.sleep(self.sleep_seconds - delay)
      now += timedelta(seconds=self.sleep_seconds)