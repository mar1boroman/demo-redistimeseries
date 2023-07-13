import redis
import json
import configparser

# Reading the config file 
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

def create_ts(stream_key):
    '''
    Ingest the data from redis stream into a timeseries key.
    Further more, 4 additional ts keys are created using compaction rules
    to hold O,C,L,H data respectively
    
    ** Notice that the 4 additional ts keys created have a common label '<stock_name>'
    ** associated with them, so that we can query them together in the future
    '''
    bucket_size_ms = 1000
    while True:
        # Read from redis stream data structure
        msg = r.xread(block=0, streams={stream_key: "$"})
        # content = json.loads(msg)
        stream_name = msg[0]
        stream_payload = stream_name[1]
        stream_ts, ts_payload = stream_payload[0]
        
        # Timeseries
        key = "ts:" + ts_payload['stock']
        ts = ts_payload['timestamp']
        value = ts_payload['price']
        
        
        # Creating parent timeseries
        
        r.ts().add(key,ts,value)
        print(f'''Processing ts key : {key} , ts : {ts}, value : {value}''')
        
        # Creating OHCL timeseries keys | Aggregation over 10 seconds
        # Note that our generator generates values at 1 second frequency by default
        
        if r.exists(f"{key}:o") == 0:
            r.ts().create(f"{key}:o", labels={'parent':key, 'type' : 'o'}) # Open
            r.ts().createrule(key, f"{key}:o", aggregation_type='first', bucket_size_msec=bucket_size_ms) # Open
        
        if r.exists(f"{key}:c") == 0:
            r.ts().create(f"{key}:c", labels={'parent':key, 'type' : 'c'}) # Close
            r.ts().createrule(key, f"{key}:c", aggregation_type='last', bucket_size_msec=bucket_size_ms) # Close
        
        if r.exists(f"{key}:l") == 0:
            r.ts().create(f"{key}:l", labels={'parent':key, 'type' : 'l'}) # Low
            r.ts().createrule(key, f"{key}:l", aggregation_type='min', bucket_size_msec=bucket_size_ms) # Low
        
        if r.exists(f"{key}:h") == 0:
            r.ts().create(f"{key}:h", labels={'parent':key, 'type' : 'h'}) # High
            r.ts().createrule(key, f"{key}:h", aggregation_type='max', bucket_size_msec=bucket_size_ms) # High

def main():
    
    
    # Read from redis source stream and create 5 timeseries keys per stock
    # ts1 : ts:<stock_name> => Holds all the data read from the stream
    # ts2 : ts:<stock_name>:o => Holds open value (ts1 compacted based on 'first' aggregation)
    # ts3 : ts:<stock_name>:c => Holds close value (ts1 compacted based on 'last' aggregation)
    # ts4 : ts:<stock_name>:l => Holds low value (ts1 compacted based on 'low' aggregation)
    # ts5 : ts:<stock_name>:h => Holds high value (ts1 compacted based on 'high' aggregation)
    # Aggregation hard coded to 1 second buckets
    create_ts('src:'+STOCK_NAME)
        
if __name__ == '__main__':
    main()