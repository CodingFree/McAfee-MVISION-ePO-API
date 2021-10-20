import argparse
import McAfeeReader

parser = argparse.ArgumentParser(description='Get and process McAfee Events from API in stream mode.')
parser.add_argument('-u','--user',help='API user',required=True)
parser.add_argument('-p','--password',help='API password',required=True)
parser.add_argument('-c','--client_id',help='API client ID',required=True)
parser.add_argument('-r','--region',help='API Tenant Region, default EU',default='EU',required=False,choices=['US','SI','EU','SY'])
parser.add_argument('-s','--sleep_seconds',help='Seconds to sleep between requests, default 10',default=10,required=False)
parser.add_argument('-m','--max_log_hours',help='Maximum log file age hours before delete it, default 12',default=12,required=False)
parser.add_argument('-S','--syslog',help='Activate syslog forward',dest='syslog',default=False,action='store_true')
parser.add_argument('-H','--syslog_server',help='Syslog server host, default 127.0.0.1',default="127.0.0.1",required=False)
parser.add_argument('-B','--syslog_protocol',help='Syslog server protocol, default TCP',default="TCP",required=False,choices=['TCP','tcp','UDP','udp'])
parser.add_argument('-P','--syslog_port',help='Syslog server port, default 25226',default=25226,required=False)



args = parser.parse_args()

reader = McAfeeReader.McAfeeReader(user=args.user,password=args.password,
    client_id=args.client_id,sleep_seconds=args.sleep_seconds,region=args.region,
    logger_name='mcafee',max_log_age_hours=args.max_log_hours,syslog=args.syslog,server=args.syslog_server,
    protocol=args.syslog_protocol,port=args.syslog_port)
reader.main()