
from appsd import select
import concurrent.futures
import time
import json
from  datetime import datetime
# Load the JSON data from the file
import pprint as pprint
import FN_calAction as ta
import locale
PER_BUY = 0.3
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

def format_currency(amount, locale_name='en_US.UTF-8'):
    # Set the locale
    locale.setlocale(locale.LC_ALL, locale_name)
    
    # Format the currency
    formatted_currency = locale.currency(amount, grouping=True)
    
    # Remove the currency symbol from the formatted string
    return formatted_currency.replace(locale.localeconv()['currency_symbol'], '').strip()

def check_value_exists(data, target_value):
      for index, entry in enumerate(data):
            #if entry <= target_value:
            #      print('*******[ close:',target_value,'ps:',entry ,' ]*******')
            if entry <= target_value:
                  return True, index
      return False, -1

def check_price_buy(data):
        try:
            priceActionLast = 999999999.99
            Order_Sell = []
            Count_Buy = 0
            Count_Sell = 0
            position = 0 # | 0 = none | 1 = B | -1 = S |
            con = 0
            
            for item in (data) :
                  close = float(item['value'])
                  time = float(item['time'])
                  
                  
                  if close <= priceActionLast:
                        priceActionLast = Cal_Buy(close)
                        Order_Sell.append(Cal_Sell(close))
                        Count_Buy += 1
                        # print("------ Cal_Buy:",close,'Sell:',Cal_Sell(close), ' | Nex B:',Cal_Buy(close))
                        
                        
                  isSell, index = check_value_exists(Order_Sell, close)
                  i =0
                  if isSell :
                        # print("------ Cal_Sell:",close, ' | Nex B:',Cal_Buy(close))
                        priceActionLast = Cal_Buy(close)
                        Order_Sell.pop(index)
                        Count_Sell += 1
                        i += 1
                
            
                  con +=1
            mony = 1850 # 50$ x37
            com = 0.2
            net = ((mony / 100)* (PER_SELL-com))
            print("ทุนต่อไม้:",mony ,"TP:",PER_SELL ,"Entry:",PER_BUY )
            print("From:",CaldateTime(data[0]['time']))
            print("to:",CaldateTime(data[len(data)-1]['time']))
            print('____________')
            print("Buy:",format_currency(Count_Buy))
            print("Sell:",format_currency(Count_Sell))
            print("รอขาย :",Count_Buy-Count_Sell,'เป็นเงิน:',format_currency((Count_Buy-Count_Sell)*mony))
            print("กำไร :",format_currency(float(Count_Sell *net))  )
            # print("รอขาย :",Order_Sell )
            
        except Exception as e:
          print('An exception occurred',e)
          #16.13 31 mil to 16.17 success
check_price_buy(select(0))



