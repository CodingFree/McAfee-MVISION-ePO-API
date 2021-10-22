import json
import requests
import logging
import sys
import time
from datetime import datetime, timedelta
import socket
import CEFProcessor
from logging import handlers

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
    API events request scope. (Default epo.evt.r dp.im.r)
  logger: Logger
    Logger object to store all logs
  auth_url: str
    URL where authorization endpoint is defined. (Default: https://iam.mcafee-cloud.com/iam/v1.0/token)
  session: requests.Session()
    Session where requests are made
  max_log_age_hours: int
    Log file hours retention. (Default: 12).
  log_file: bool
    Store program logs also to a file. (Default: False)

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
  def __init__(self,user,password,client_id,sleep_seconds=10,region='EU',scope='epo.evt.r dp.im.r',
         logger_name='mcafee',max_log_age_hours=12,syslog=False,server="localhost",protocol="TCP",port=514,log_file=False):
    self.logger = logging.getLogger(logger_name)
    self.logger.setLevel('INFO')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)

    ### Configuring log store to file
    self.log_file = log_file
    if self.log_file:
      handler = logging.FileHandler("/var/log/mcafee-collector/mcafee-collector.log")
      formatter = logging.Formatter("%(asctime)s - McAfeeReader [%(levelname)s] %(message)s")
      handler.setFormatter(formatter)
      self.logger.addHandler(handler)
    
    ### Configuring Syslog forwarding
    self.syslog = syslog
    if self.syslog:
      if protocol.lower() == "tcp":
        self.handler = logging.handlers.SysLogHandler(address=(server,port),socktype=socket.SOCK_STREAM)
        self.handler.setFormatter(logging.Formatter('%(message)s\n'))
        self.handler.append_nul = False
      elif protocol.lower() == "udp":
        self.handler = logging.handlers.SysLogHandler(address=(server,port))
      else:
        self.logger.critical("Syslog protocol not valid.")
        sys.exit(1)
      self.syslog_logger = logging.getLogger("syslog")
      self.syslog_logger.setLevel(logging.DEBUG)
      self.syslog_logger.addHandler(self.handler)
      self.logger.info("Successfully created logger instance for syslog {0}".format(protocol+'://'+server+':'+str(port)))

    ### Configuring file forwarding
    self.max_log_age_hours = max_log_age_hours

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
    self.sleep_seconds = int(sleep_seconds)
    self.session = requests.Session()
    self.session.headers = headers
    
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
      sys.exit(1)
  
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
    }

    res = self.session.get('https://{0}/eventservice/api/v2/events'.format(self.base), params=params)

    if res.ok:
      return res.json()
    else:
      self.logger.error('Could not retrieve MVISION EPO Events. {0} - {1}'.format(str(res.status_code),res.text))
      sys.exit(1)
      
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

  def write_syslog(self,evts):
    """
    Writes events received to a file
    
    Parameters
    ----------
    evts : list
      Events to write
    """
    for event in evts:
      try:
        self.syslog_logger.info(event)
      except Exception as e:
        self.logger.error("Error sending log to syslog server - {0}".format(str(e)))
    
        
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
    attribs = {
      "deviceVendor": "McAfee",
      "deviceId": "McAfee EPO",
      "deviceVersion": "MVISION",
      "timeKey": "receivedutc",
      "hostKey": "sourcehostname",
      "severityKey": "threatseverity",
      "typeKey": "threattype",
      "subTypeKey": "threatcategory",
      "signatureIdKey": "threateventid",
    }
   
    now = datetime.utcnow()
    end_hour = (now.hour + 2) % 24 # renew auth token each 2 hours
    # Local file options
    rotation_hour = (now.hour + self.max_log_age_hours) % 24

    while True:
      delay_begin = time.time()
      # calculates loop requested times (since -> since + sleep time)
      until_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
      since_iso = (now - timedelta(seconds=self.sleep_seconds)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
      # retrieve events and write them to file
      events = self.events(since=since_iso,until=until_iso)
      # convert events to CEF format using CEFProcessor module
      cef_events = CEFProcessor.CEFProcessor(events['Threats'],attribs=attribs,log_file=self.log_file).process_events()
      # Working on DLP events processing
      cef_events += CEFProcessor.CEFProcessor(events['Incidents'],attribs=attribs,log_file=self.log_file).process_events()
      # if day has finished, recreate token auth and restart end_hour variable
      if now.hour == end_hour:
        self.auth()
        end_hour = (now.hour + 2) % 24 # renew auth token each 2 hours
      if self.syslog:
        self.write_syslog(cef_events)
      else:
        self.write(cef_events,now)
        # check if rotation time has arrived and then checks every hour
        if now.hour == rotation_hour:
          self.rotate()
          rotation_hour = (now.hour + 1) % 2
      # to avoid events loss, uses loop execution time to substract it to wait time
      delay = time.time() - delay_begin
      time.sleep(self.sleep_seconds - delay)
      now += timedelta(seconds=self.sleep_seconds)