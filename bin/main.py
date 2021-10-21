import argparse
import McAfeeReader
import re
def read_properties(file,args):
    mapping = {
        'MCAFEE_USER': 'user',
        'MCAFEE_PASSWORD': 'password',
        'MCAFEE_CLIENT_ID': 'password',
        'LOG_FILE_OPT': 'log_file',
        'MCAFEE_REGION': 'region',
        'SLEEP_SECONDS': 'sleep_seconds',
        'MAX_LOG_HOURS': 'max_log_hours',
        'SYSLOG': 'syslog',
        'SYSLOG_SERVER': 'syslog_server',
        'SYSLOG_PROTOCOL': 'syslog_protocol',
        'SYSLOG_PORT': 'syslog_port'
    }
    with open(file,'r') as f:
        for line in f:
            if re.match(r"[\s\t]*#.*",line) == None: # skipping comment lines
                try:
                    k,value = line.split('=')
                    if k in mapping.keys():
                        vars(args)[mapping[k]] = value
                except Exception as e:
                    print("Error in configuration file format in line: {0}".format(line))
                    print("Skipping this line")
    return args

parser = argparse.ArgumentParser(description='Get and process McAfee Events from API in stream mode.')
parser.add_argument('-u','--user',help='API user',required=False)
parser.add_argument('-p','--password',help='API password',required=False)
parser.add_argument('-c','--client_id',help='API client ID',required=False)
parser.add_argument('-r','--region',help='API Tenant Region, default EU',default='EU',required=False,choices=['US','SI','EU','SY'])
parser.add_argument('-s','--sleep_seconds',help='Seconds to sleep between requests, default 10',default=10,required=False)
parser.add_argument('-m','--max_log_hours',help='Maximum log file age hours before delete it, default 12',default=12,required=False)
parser.add_argument('-S','--syslog',help='Activate syslog forward',dest='syslog',default=False,action='store_true')
parser.add_argument('-H','--syslog_server',help='Syslog server host, default 127.0.0.1',default="127.0.0.1",required=False)
parser.add_argument('-B','--syslog_protocol',help='Syslog server protocol, default TCP',default="TCP",required=False,choices=['TCP','tcp','UDP','udp'])
parser.add_argument('-P','--syslog_port',help='Syslog server port, default 25226',default=25226,required=False)
parser.add_argument('-l','--log_file',help='Save program logs to file (/var/log/mcafee-collector/mcafee-collector.log) or just to stdout',required=False,action='store_true')
parser.add_argument('-f','--conf_file',help='Configuration file where to read properties',required=False)

args = parser.parse_args()

if args.conf_file != "":
    args = read_properties(args.conf_file,args)

reader = McAfeeReader.McAfeeReader(user=args.user,password=args.password,
    client_id=args.client_id,sleep_seconds=args.sleep_seconds,region=args.region,
    logger_name='mcafee',max_log_age_hours=args.max_log_hours,syslog=args.syslog,server=args.syslog_server,
    protocol=args.syslog_protocol,port=args.syslog_port,log_file=args.log_file)
reader.main()