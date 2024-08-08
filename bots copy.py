
from appsd import select
import concurrent.futures
import time
import json
from  datetime import datetime
# Load the JSON data from the file
import pprint as pprint
import FN_calAction as ta

PER_BUY = 0.45
PER_SELL = 0.55

def CaldateTime(timestamp):
    # Convert the timestamp to a datetime object
    original_datetime = datetime.fromtimestamp(timestamp)
    
    # Print the current datetime and the adjusted datetime
    #print("Original datetime:", original_datetime)
    
    return original_datetime
def Cal_Buy(price):
      p = float(price) -( (price / 100 )* PER_BUY )
      return round(p, 4)

def Cal_Sell(price):
      p = float(price) +( (price / 100 )* PER_SELL )
      return round(p, 4)


def check_price_buy(data):
        try:
            priceActionLast = 999999999.99
            Order_Sell = []
            Count_Buy = 0
            Buy = 0
            Count_Sell = 0
            position = 0 # | 0 = none | 1 = B | -1 = S |
            con = 0
            for item in data:
                 
                  price = float(item['value'])
                  # GET ALL Price SELL to Action Sell
                  print(CaldateTime(item['time']),price)
                  if len(Order_Sell) > 0:
                        i = 1
                        while i <= len(Order_Sell):
                              # print(i , len(Order_Sell))
                             
                              PS = Order_Sell[i-1]
                              if price >= PS:
                                    # print(con,"Action Sell : " ,price ,' > ',PS)
                                    # print("Order_Sell  : " ,len(Order_Sell))
                                    priceActionLast = Cal_Buy(price) 
                                    Count_Sell += 1
                                    #เมื่อ Order นั้นซื้อแล้วให้ลบ
                                    Order_Sell.pop(i-1)  # Remove the current item
                              
                              else:
                                  i += 1  # Only increment the index if no item was removed
                  # Action Buy
                  if price <= priceActionLast :
                       
                        # Buy
                        priceActionLast = Cal_Buy(price) 
                        Buy = price
                        Count_Buy += 1
                        position = 1
                        # ตั้งราคาขาย
                        sell_P = Cal_Sell(Buy)
                        # print(con,"Action Buy : " ,price ,'<',priceActionLast," | Price Sell : ",sell_P,'lastAction :',priceActionLast)
                        Order_Sell.append(sell_P)
                        
                  
                 
                 
                  con +=1
            print("Buy:",Count_Buy)
            print("Sell:",Count_Sell)
            print("รอขาย :",Count_Buy-Count_Sell)
            
        except Exception as e:
          print('An exception occurred',e)
          
check_price_buy(select(10))