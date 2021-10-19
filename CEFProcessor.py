import datetime
from dateutil import parser
import logging

class CEFProcessor():
  """
  A class used to parse a JSON file and convert it on CEF format

  ...

  Attributes
  ----------
  hostDefault: str
    Default host to append if not present on the log (Default "HOST")
  severityDefault: str
    Default severity to append if not present on the log (Default "1")
  signatureIdDefault: str
    Default signature ID to append if not present on the log (Default "000001")
  eventsKey: str
    Key where events are stored in input JSON
  attribs: dictionary
    Dictionary containing all default properties and default log keys to create CEF log.
    This dictionary must contain the following keys: deviceVendor, deviceId, deviceVersion, timeKey, hostKey, severityKey and signatureIdKey
    An example could be:
      attribs = {
        "deviceVendor": "McAfee",
        "deviceId": "McAfee EPO",
        "deviceVersion": "SaaS",
        "timeKey": "EventTime",
        "hostKey": "ServerID",
        "severityKey": "ThreatSeverity",
        "signatureIdKey": "AutoID",
      }
  fullFormat: Boolean
    Configures if the CEF output should have the full format (<time> <host> <CEF message>) or just the CEF message (Default True)
  messages: List
    Contains the list of CEF format messages once JSON is processed
  logger: Logger
    Logger object to store all logs

  Methods
  -------
  process_<field>(event,<field>Key)
    A set of functions that process some fields and assigns its default values if not found on the dictionary
  process_messages()
    Function that process all JSON messages and returns a list of them in CEF format.
  """
  def __init__(self,events,attribs,fullFormat=True,eventsKey="Events",hostDefault="Analyzer",
         severityDefault="1",signatureIdDefault="000001",logger_name="cefprocessor"):
  ##### TODO: to be redefined when got a log example from McAfee API
    """
    Parameters
    ----------
    events : list
      List of events to process
    Rest of the class attributes needed.
    """
    self.hostDefault = hostDefault
    self.severityDefault = severityDefault
    self.signatureIdDefault = signatureIdDefault
    self.eventsKey = eventsKey
    self.attribs = attribs
    self.fullFormat = fullFormat
    self.messages = []
    self.events = events

    self.logger = logging.getLogger(logger_name)
    self.logger.setLevel('INFO')
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)

    self.logger.debug("Starting CEFProcessor with parameters: hostDefault={0},severityDefault={1},\
      signatureIdDefault={2},eventsKey={3},attribs={4}, fullFormat = {5}\
      ".format(hostDefault,severityDefault,signatureIdDefault,eventsKey,attribs,fullFormat))
  
  def process_time(self,event,timeKey):
    if timeKey in event.keys():
      time = parser.parse(event[timeKey]["value"])
    else:
      time = datetime.datetime.now()
    return time.strftime("%b %d %H:%M:%S")
    
  def process_host(self,event,hostKey):
    if hostKey in event.keys():
      host = event[hostKey]["value"]
    else:
      host = self.hostDefault
    return host

  def process_severity(self,event,severityKey):
    if severityKey in event.keys():
      severity = event[severityKey]["value"]
    else:
      severity = self.severityDefault
    return severity

  def process_signature(self,event,signatureKey):
    if signatureKey in event.keys():
      signature = event[signatureKey]["value"]
    else:
      signature = self.severityDefault
    return signature

  def process_events(self):
    messages = []
    for ev in self.events[self.eventsKey]:
      try:
        time = self.process_time(ev,self.attribs["timeKey"])
        host = self.process_host(ev,self.attribs["hostKey"])
        severity = self.process_severity(ev,self.attribs["severityKey"])
        name = ev[self.attribs["typeKey"]]["value"] + ":" + ev[self.attribs["subTypeKey"]]["value"]
        signature = self.process_signature(ev,self.attribs["signatureIdKey"])
        cef = "CEF:0|%s|%s|%s|%s|%s|%s|" % (self.attribs["deviceVendor"],self.attribs["deviceId"],
                              self.attribs["deviceVersion"],signature,name,severity)
        if self.fullFormat:
          cef = "%s %s " % (time,host) + cef
        for k,v in ev.items():
          if k not in attribs.values():
            cef += "%s=%s " % (k,v)
        if cef[-1] == " ":
          cef = cef[:-1]
        messages.append(cef)
      except Exception as e:
        self.logger.error("Error processing messages - {0}".format(str(e)))
    self.messages = messages
    self.logger.debug("Logs correctly processed")
    return self.messages