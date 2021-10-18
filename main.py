import McAfeeReader
import argparse

parser = argparse.ArgumentParser(description='Get and process McAfee Events from API in stream mode.')
parser.add_argument('-u','--user',help='API user',required=True)
parser.add_argument('-p','--password',help='API password',required=True)
parser.add_argument('-c','--client_id',help='API client ID',required=True)
parser.add_argument('-r','--region',help='API Tenant Region, default EU',default='EU',required=False,choices=['US','SI','EU','SY'])
parser.add_argument('-s','--sleep_seconds',help='Seconds to sleep between requests, default 10',default=10,required=False)
parser.add_argument('-m','--max_log_hours',help='Maximum log file age hours before delete it, default 12',default=12,required=False)
args = parser.parse_args()

reader = McAfeeReader.McAfeeReader(user=args.user,password=args.password,
    client_id=args.client_id,sleep_seconds=args.sleep_seconds,region=args.region,scope='epo.evt.r',
    logger_name='mcafee',max_log_age_hours=args.max_log_hours)
reader.main()