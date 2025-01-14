# McAfee Events API recollector and processor
## Installation
To install collector, you can run the installation provided script in this way:
```bash
bash mcafee-collector-install.sh <API user> <API password> <API client_id> <program logs to file {-y,-n}>
```
Script mandaroty options are:
* API user: User to connect to the API
* API password: Password to connect to the API
* API client_id: Client ID used to connecto to the API. Could be obtained from https://auth.ui.mcafee.com/support.html
* Program logs to file: Store program logs to /var/log/mcafee-collector/mcafee-collector.log (-y) or not (-n)
## Single usage
```bash
usage: /opt/mcafee-collector/bin/main.py [-h] -u USER -p PASSWORD -c CLIENT_ID [-r {US,SI,EU,SY}]
               [-s SLEEP_SECONDS] [-m MAX_LOG_HOURS] [-S] [-H SYSLOG_SERVER]
               [-B {TCP,tcp,UDP,udp}] [-P SYSLOG_PORT] [-l]

Get and process McAfee Events from API in stream mode.

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  API user
  -p PASSWORD, --password PASSWORD
                        API password
  -c CLIENT_ID, --client_id CLIENT_ID
                        API client ID
  -r {US,SI,EU,SY}, --region {US,SI,EU,SY}
                        API Tenant Region, default EU
  -s SLEEP_SECONDS, --sleep_seconds SLEEP_SECONDS
                        Seconds to sleep between requests, default 10
  -m MAX_LOG_HOURS, --max_log_hours MAX_LOG_HOURS
                        Maximum log file age hours before delete it, default
                        12
  -S, --syslog          Activate syslog forward
  -H SYSLOG_SERVER, --syslog_server SYSLOG_SERVER
                        Syslog server host, default 127.0.0.1
  -B {TCP,tcp,UDP,udp}, --syslog_protocol {TCP,tcp,UDP,udp}
                        Syslog server protocol, default TCP
  -P SYSLOG_PORT, --syslog_port SYSLOG_PORT
                        Syslog server port, default 25226
  -l, --log_file        Save program logs to file (/var/log/mcafee-
                        collector/mcafee-collector.log) or just to stdout

```
## File configuration
Main binary could be executed and configured by using flag parameters but it could be also configured by using a configuration file. This configuration file must be in KEY=VALUE format (environmental variables format) and accept the following parameters mapping with the flag specified:
```
MCAFEE_USER: user
MCAFEE_PASSWORD: password
MCAFEE_CLIENT_ID: password
LOG_FILE_OPT: log_file
MCAFEE_REGION: region
SLEEP_SECONDS: sleep_seconds
MAX_LOG_HOURS: max_log_hours
SYSLOG: syslog
SYSLOG_SERVER: syslog_server
SYSLOG_PROTOCOL: syslog_protocol
SYSLOG_PORT: syslog_port
```
This file also support comments by using #.
If LOG_FILE_OPT or SYSLOG options are present on the configuration file, as they are boolean options, they will be evaluated as True. If they are not needed, do not put them into configuration file. Its values will be skipped.
An example of this file is:
```file
MCAFEE_USER=user
# password configuration
MCAFEE_PASSWORD=password
LOG_FILE_OPT=
SLEEP_SECONDS=10
```
Note: If a configuration file is used, it will override all parameters passed as argument that are present on the configuration file. The rest of the arguments are not modified.