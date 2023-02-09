import platform

import aiohttp
import asyncio
import pathlib
import sys
import json
from datetime import date, timedelta
import re

BASE_DIR = pathlib.Path()

async def main(quantity_days):
    
    async with aiohttp.ClientSession() as session:       
             
        param = {"date": "08.02.2023"}
        
        today = date.today()
        quantity_days = 3
        while quantity_days != 0:
            days = quantity_days
            pre_day = (today - timedelta(days)).strftime("%d.%m.%Y")
            quantity_days -= 1 
            print(pre_day)
            
    
        try:           
            async with session.get("https://api.privatbank.ua/p24api/exchange_rates?", params = param) as response:
                if response.status == 200:
                    result = await response.json()
                    #print(result)
                    
                    def find_currency(requested_currency: str) -> dict: #знайти валюту в даних від приватбанку
                        i = 0
                        length_exchangeRate = len(result.get("exchangeRate"))
                        while result.get("exchangeRate")[i].get("currency") != requested_currency:
                            i += 1
                            if i == length_exchangeRate:
                                print("Requested currency is not correct")
                                return None
                                
                        requested_currency_Rate = result.get("exchangeRate")[i]
                        
                        print(requested_currency_Rate)
                        return requested_currency_Rate
                    
                    def read_json_file(): #читання даних з файла json
                        with open(BASE_DIR.joinpath("storage/data.json"), 'r', encoding='utf-8') as fd:
                            text = fd.readline()
                            if text:
                                upload = json.loads(text)  
                        return upload
                    
                    def write_json_file(output): #запис даних до файла json 
                        upload = read_json_file()         
                        with open(BASE_DIR.joinpath("storage/data.json"), 'w', encoding='utf-8') as fd:                
                            upload.append(output)
                            json.dump(upload, fd, ensure_ascii=False) 
                    
                    def output_for_file():
                        all_value_Rates = {}
                        for i in ["EUR", "USD"]: 
                            answer_currency_Rate = find_currency(i)
                            value_Rate = {
                                answer_currency_Rate.get("currency"): {
                                    "sale": answer_currency_Rate.get("saleRate"), 
                                    "purchase": answer_currency_Rate.get("purchaseRate")
                                }
                            }
                            all_value_Rates.update(value_Rate)
   
                        output = {
                            pre_day: all_value_Rates
                            }
                        print([output]) 
                        write_json_file(output)
                        
                        return
                            
                    output_for_file()
                               
                else:
                    print(f"Error status: {response.status}")
        except aiohttp.ClientConnectorError as err:            
                print(f"Connection error:", str(err))
                #print(response.ok)
                
                #return result


if __name__ == "__main__":
    STORAGE_DIR = pathlib.Path().joinpath('storage')
    FILE_STORAGE = STORAGE_DIR / 'data.json'
    
    if not FILE_STORAGE.exists():
        with open(FILE_STORAGE, 'w', encoding='utf-8') as fd:
            json.dump([], fd, ensure_ascii=False)
    try:
       # num = sys.argv[1]
       num = 2
    except ValueError:
        print("Entered count days to get request")        
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main(num))