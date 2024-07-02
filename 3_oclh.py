import redis
from time import sleep
import configparser

parser = configparser.ConfigParser()
parser.read_file(open("config.ini"))

for x, y in parser.items("GENERAL"):
    if x == 'stock_name':
        STOCK_NAME = y
    if x == 'redis_host':
        redis_host = y
    if x == 'redis_port':
        redis_port = y
        
# Connecting to redis       
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

def view_oclh(tskey):
    '''
    TS.MGET
    =======
    This function queries all the 4 O,C,L,H compacted keys which have the label 'ts:<stock_name>',
    combines their respones,
    and loads the response into a redis stream data structure
    which can be used in the ui.
    
    Notice the use of 'maxlen' and 'approximate' parameters
    These help the ui stream evict the old entries automatically,
    thus making sure your memory consumption does not explode
    '''
    prev_bucket = None
    while True:
        resp = r.ts().mget([f'parent={tskey}'],)
        payload = {}
        payload['stock'] = tskey.split(':')[1]
        for agg in resp:
            for k,v in agg.items():
                if k == f'{tskey}:o':
                    payload['ts'] = v[1]
                    payload['open'] = v[2]
                if k == f'{tskey}:c':
                    payload['ts'] = v[1]
                    payload['close'] = v[2]
                if k == f'{tskey}:l':
                    payload['ts'] = v[1]
                    payload['low'] = v[2]
                if k == f'{tskey}:h':
                    payload['ts'] = v[1]
                    payload['high'] = v[2]

        if payload['ts'] == prev_bucket:
            continue
        else:
            print(payload)
            r.xadd(f'ui:{tskey}', payload, id=payload['ts'],maxlen=10000,approximate=True)
            prev_bucket = payload['ts']
        sleep(1.01)
    

def main():
    # Combine the data from the above 4 oclh streams
    # Push them into a target stream and display every 10 seconds
    # Note : Since our downsampling freq is 10 seconds, we would enter data into stream >= 10 sec frequency
    
    view_oclh('ts:'+STOCK_NAME)
        
if __name__ == '__main__':
    main()