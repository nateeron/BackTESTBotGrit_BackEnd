import requests
import pandas as pd
import sqlite3
from pprint import pprint
# Define the base URL and parameters
from datetime import datetime,timedelta
import locale
import threading
import time
import websocket
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from flask_cors import CORS
from starlette.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor, as_completed
#import bots as b
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; specify domains as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)



base_url = "https://api.binance.com/api/v3/klines"
symbol = 'XRPUSDT'
interval = '1s'  # Interval for candlesticks
limit = 5  # Number of data points to fetch
lengtbar = 15

    
CONN = sqlite3.connect('crypto_prices.db')

def CaldateTimessss(number):
    start_datetime = datetime.now()
    start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    new_datetime = start_datetime - timedelta(days=number)
    # print("now:",start_datetime)
    # print("to :",new_datetime)
    return new_datetime
def CaldateTime_1000(timestamp):
    # Convert the timestamp to a datetime object
    original_datetime = datetime.fromtimestamp(timestamp / 1000.0)
    
    # Print the current datetime and the adjusted datetime
    #print("Original datetime:", original_datetime)
    
    return original_datetime

def CaldateTime(timestamp):
    # Convert the timestamp to a datetime object
    original_datetime = datetime.fromtimestamp(timestamp)
    
    # Print the current datetime and the adjusted datetime
    #print("Original datetime:", original_datetime)
    
    return original_datetime
def StartNewTime(interval, factor):
    # Define the number of seconds per interval unit
    intervalUnits = {
        's': 1,         # Seconds
        'm': 60,        # Minutes
        'h': 3600,      # Hours
        'd': 86400,     # Days
        'w': 604800     # Weeks
    }
    
    # Parse the interval to get the number and the unit
    intervalValue = int(interval[:-1])
    intervalUnit = interval[-1]
    
    # Calculate the total number of milliseconds
    totalMilliseconds = intervalValue * intervalUnits[intervalUnit] * factor * 1000
    
    return totalMilliseconds



def load_data(symbol, interval, limit, lastEndTime):
    
    params = {
         
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
    if lastEndTime != 0:
        params['startTime'] = lastEndTime
        
    response = requests.get(base_url, params=params)
    data = []
    if response.status_code == 200:
        data = response.json()
      
    
    return data

def SortData(data):
    sortedData = sorted(data, key=lambda x: x[0])
    return sortedData

def get_data(lengtbar_ ,limit_ ,starttime = 0):
    print('------------------------------------------------------------')
    print('get_data : ',lengtbar_ ,limit_ ,starttime,CaldateTime(starttime))
    print('------------------------------------------------------------')
    num_batches = int(lengtbar_ / limit_)
    data_ALL = []
    lastEndTime = 0
    print("download.....")
    loadTime= []
    # หาค่า เวลา แล้วกระจาย Load
    for _ in range(num_batches):
        
        if _ == 0 and starttime == 0:
            # --------------------------------------------------
            x = load_data(symbol, interval, limit_, lastEndTime)
            data_ALL.extend(x)  # Use extend to add elements of x to data_ALL
            
            if len(x) > 0 :
                st = StartNewTime(interval, limit_)
                lastEndTime = x[0][0] - st
                loadTime.append(lastEndTime)
            # --------------------------------------------------
        else:
            if starttime != 0 :
                # 1723104392000
                # 1723104387
                print(starttime,CaldateTime(starttime))
                st = StartNewTime(interval, limit_)
                loadTime.append((int(starttime)*1000)- st)
                print(loadTime[0],CaldateTime(loadTime[0]/1000))
                
                starttime = 0
            else:
                st = StartNewTime(interval, limit_)
                lastEndTime = loadTime[len(loadTime)-1] - st
                loadTime.append(lastEndTime)
            
    # print(loadTime)
    
    # Use concurrent futures for batch requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_time = {executor.submit(load_data, symbol, interval, limit_, time): time for time in loadTime}
        for future in as_completed(future_to_time):
            time = future_to_time[future]
            try:
                data = future.result()
                data_ALL.extend(data)
               
            except Exception as e:
                print(f"Request failed for time {time}: {e}")
    #print(CaldateTime(time))
    
    # for item in data_ALL:
    #     print(CaldateTime(item[0]))
    print("SortData ...")
    resp = SortData(data_ALL)
    print("download Success...")
    # for item in resp:
    #     print(CaldateTime(item[0]))
    #------------------------------------
    insert(resp)
    return resp
    
# get_data(5000000,1000)





def CreateTable():
    cursor = CONN.cursor()
    
    cursor.execute('''
             CREATE TABLE IF NOT EXISTS tb_price (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 timestem DATETIME,
                 close REAL
             )
         ''')
    CONN.commit()
    CONN.close()
    
    
def insert(data):
         # Connect to the SQLite database (or create it if it doesn't exist)
        CONN = sqlite3.connect('crypto_prices.db')
        print('insert.....',len(data))
        cursor = CONN.cursor()
        # Insert data into the table
        for row in data:
            cursor.execute('''
                INSERT INTO tb_price (timestem, close)
                VALUES (?,  ?)
            ''', (row[0],  row[4]))

        # Commit the changes and close the connection
        CONN.commit()
        CONN.close()
  
def format_currency(amount, locale_name='en_US.UTF-8'):
    # Set the locale
    locale.setlocale(locale.LC_ALL, locale_name)
    
    # Format the currency
    formatted_currency = locale.currency(amount, grouping=True)
    
    # Remove the currency symbol from the formatted string
    return formatted_currency.replace(locale.localeconv()['currency_symbol'], '').strip()



def select(limit):
    cs = sqlite3.connect('crypto_prices.db')
    cursor = cs.cursor()
    lm = ''
    if limit > 0 :
        lm = f'limit {limit}'
    qury = f''' select * From  tb_price order by timestem {lm}'''
    
    cursor.execute(qury)
    data = cursor.fetchall()
    # print(data)
    print("------------------------------------")
    
    oj_ALL = []
    for item in data:
        oj = {}
        # print(CaldateTime(item[1]),item[2])
        oj["time"] = int(item[1]/1000)
        oj["value"] = item[2]
        oj_ALL.append(oj)
    cs.close()
    print("Data : ",format_currency(len(oj_ALL)))
    # print(oj_ALL)
    
    return oj_ALL

def delete():
    CONN = sqlite3.connect('crypto_prices.db')
    cursor = CONN.cursor()
      
    cursor.execute('''DELETE FROM tb_price ''')

    # Commit the changes and close the connection
    CONN.commit()
    CONN.close()
        
class req(BaseModel):
    ok: str
    limit:int
    lengtbar:int
    
class req_select(BaseModel):
    limit:int
    
    
    
    
    
@app.post("/load")
def LoadNex(req: req):
    limit_ = req.limit
    lengtbar_ = req.lengtbar
    data = select(limit_)
    t1 =0
    if len(data) != 0:
        t1 = data[0]['time']
        t2 = data[len(data)-1]['time']
        print(t1,CaldateTime(t1))
        print(t2,CaldateTime(t2))
    get_data(lengtbar_ ,limit_,t1)
    return data
   
@app.get("/ch_date")
def ch_date():
    data = select(0)
    se = []
    print('Lendata :',len(data))
    for item in data:
        se.append(CaldateTime(item['time'])) 
        print(CaldateTime(item['time']))
        
    return se
   
@app.get("/count")
def count_data():
    data = select(0)
    return len(data)
   
@app.post("/xrp")
def getxrp(req: req_select):
    limit_ = req.limit
    return select(limit_)

@app.get("/xrp")
def getxrp():
    return select(200000)

@app.get("/delete")
def getxrp():
    delete()
    return 'success'

@app.get("/bot")
def getxrp_bot():
    data = select(200000)
   # b.bot(data)
    return 'success'


@app.post("/insert")
def posxrp(req: req):
   
    # print(req.ok)
    lengtbar_ = req.lengtbar
    limit_ = req.limit
    get_data(lengtbar_ ,limit_)
    return "OK"

# CreateTable()
#insert()
# select()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,  port=8400)