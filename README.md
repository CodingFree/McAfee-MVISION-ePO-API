# McAfee Events API recollector and processor
## Installation
To install collector, you can run the installation provided script in this way:
```bash
bash mcafee-collector-install.sh <API user> <API password> <API client_id> <program logs to file {-y,-n}>
```
## Single Usage
```bash
usage: main.py [-h] -u USER -p PASSWORD -c CLIENT_ID [-r {US,SI,EU,SY}] [-s SLEEP_SECONDS] [-m MAX_LOG_HOURS] [-S]
               [-H SYSLOG_SERVER] [-B {TCP,tcp,UDP,udp}] [-P SYSLOG_PORT]

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
                        Maximum log file age hours before delete it, default 12
  -S, --syslog          Activate syslog forward
  -H SYSLOG_SERVER, --syslog_server SYSLOG_SERVER
                        Syslog server host
  -B {TCP,tcp,UDP,udp}, --syslog_protocol {TCP,tcp,UDP,udp}
                        Syslog server protocol
  -P SYSLOG_PORT, --syslog_port SYSLOG_PORT
                        Syslog server port
```