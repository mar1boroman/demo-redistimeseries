# demo-redistimeseries
A simple way to design OCLH charts using Redis Timeseries module

Note that this is not a production ready code, this is just a demo
of how Redis Streams work with Redis Timeseries to enable OCLH charts

# How to run this demo

## Clone the repository and install the required libraries
```
git clone https://github.com/mar1boroman/demo-redistimeseries.git && cd demo-redistimeseries
```

Prepare and activate the virtual environment

```
python3 -m venv .env && source .env/bin/activate
```

Install necessary libraries and dependencies

```
pip install -r requirements.txt
```

## Run scripts on seperate terminals

### Terminal 1

```
python 1_gen.py
```

### Terminal 2

```
python 2_ts.py
```

### Terminal 3

```
python 3_oclh.py
```

# Visualizing in Grafana

If you have grafana installed, you can configure your redis datasource and import the [Stock OCLH grafana](./Stock%20Prices%20OCLH-grafana.json) to visualize the stream using XRANGE command

# Code Explanation

## 1_gen.py

This script generates mock stock data and pushes it into a redis stream datastructure

## 2_ts.py

This script reads from the redis stream created in step 1 and creates 5 timeseries keys
- ts1 : ts:<stock_name> => Holds all the data read from the stream
- ts2 : ts:<stock_name>:o => Holds open value (ts1 compacted based on 'first' aggregation) [Label=ts:<stock_name>]
- ts3 : ts:<stock_name>:c => Holds close value (ts1 compacted based on 'last' aggregation) [Label=ts:<stock_name>]
- ts4 : ts:<stock_name>:l => Holds low value (ts1 compacted based on 'low' aggregation) [Label=ts:<stock_name>]
- ts5 : ts:<stock_name>:h => Holds high value (ts1 compacted based on 'high' aggregation) [Label=ts:<stock_name>]

## 3_oclh.py

This script performs TS.MGET based on [Label=ts:<stock_name>] and combines the data from ts2, ts3, ts4, ts5
and writes the OCLH payload into a redis stream data structure 'ui:ts:<STOCK_NAME>'