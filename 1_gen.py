import time
import random
from time import sleep
import redis
from multiprocessing import Process
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
        
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

def generate_ticks(stock_name):
    while True:
        yield {
            'timestamp' : int(time.time() * 1000),
            'stock' : stock_name,
            'price' : round(random.uniform(1.0, 100.0),2),
            'size' : random.randint(10,1000)
        }

def load_redis_source_stream(stream_name:str):
    stock_name = stream_name.split(":")[1]
    print(f"Generating random stock data for {stock_name}")
    for payload in generate_ticks(stock_name):
        sleep(0.1) # Slowing the producer, since consumer needs to be scaled if exceeded
        print(payload)
        r.xadd(
            stream_name,
            payload
        )
        
if __name__ == "__main__":
    # Cleanup
    r.flushdb()
    # Load redis source stream
    load_redis_source_stream('src:'+STOCK_NAME) # Load redis stream with mock stock json payload every 1 second
