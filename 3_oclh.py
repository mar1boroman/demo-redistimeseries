import redis
import json
from time import sleep

STOCK_NAME = 'MyStock'
r = redis.Redis(host='redis-14916.okon.demo.redislabs.com', port=14916, decode_responses=True)

def view_oclh(tskey):
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

        print(payload)
        r.xadd(f'ui:{tskey}', payload, id=payload['ts'],)
        sleep(1.01)
    

def main():
    # Combine the data from the above 4 oclh streams
    # Push them into a target stream and display every 10 seconds
    # Note : Since our downsampling freq is 10 seconds, we would enter data into stream >= 10 sec frequency
    
    view_oclh('ts:'+STOCK_NAME)
        
if __name__ == '__main__':
    main()