import platform
import aiohttp
import asyncio
import pathlib
import sys
import json
from datetime import date, timedelta
from aiopath import AsyncPath
from aiofile import async_open
import logging

#BASE_DIR = pathlib.Path()
#BASE_DIR.joinpath("storage/data.json")

async def request(param_list):
    async with aiohttp.ClientSession() as session:    
        for param in param_list:  
            try:           
                async with session.get("https://api.privatbank.ua/p24api/exchange_rates?", params = param) as response:
                    if response.status == 200:
                        result = await response.json()
                        output_data(result)
                    else: 
                        logging.error(f"Error status: {response.status}")
            except aiohttp.ClientConnectorError as err: 
                logging.error(f"Connection error: {err}")
    return None
    
def find_currency(requested_currency: str, answer: dict) -> dict: #знайти валюту в даних від приватбанку
    i = 0
    length_exchangeRate = len(answer.get("exchangeRate"))
    while answer.get("exchangeRate")[i].get("currency") != requested_currency:
        i += 1
        if i == length_exchangeRate:
            print("Requested currency is not correct")
            return None
            
    requested_currency_Rate = answer.get("exchangeRate")[i]       
    return requested_currency_Rate, answer.get("date")    
    
#формується параметр дати для запиту данних в API
#param = {"date": "10.02.2023"}   - приклад необхідного формату (на поточну дату відповідь сервера - 500???)
async def date_param(quantity_days): 
    quantity_days = int(quantity_days)
    today = date.today()
    param_list = []
    while quantity_days != 0:
        days = quantity_days
        pre_day = (today - timedelta(days)).strftime("%d.%m.%Y")
        quantity_days -= 1 
        param = {"date": pre_day}   
        param_list.append(param) 
    await request(param_list)
    return None

# async def write_json_file(filename: str, queue: asyncio.Queue): #запис даних до файла json        
#     async with async_open(filename, 'w', encoding='utf-8') as afd:                
#         upload.append(output)
#         json.dump(upload, afd, ensure_ascii=False) 
                
# async def read_json_file(file: AsyncPath, queue: asyncio.Queue): #читання даних з файла json
#     async with async_open(file, 'r', encoding='utf-8') as afd:
#         text = afd.readline()
#         if text:
#             upload = json.loads(text)  
#     return upload

def output_data(answer):
    all_value_Rates = {}
    for i in ["EUR", "USD"]: 
        answer_currency_Rate, date = find_currency(i, answer)
        value_Rate = {
            answer_currency_Rate.get("currency"): {
                "sale": answer_currency_Rate.get("saleRate"), 
                "purchase": answer_currency_Rate.get("purchaseRate")
            }
        }
        all_value_Rates.update(value_Rate)

    output = {
        date: all_value_Rates
        }
    print([output]) 
    return #write_json_file(output)               

async def main(num):
    if 0 <= int(num) <= 10: 
        await date_param(num)
    else:    
        print("Quantity days must be between 1 and 10")
    return None
    

# async def run():
#     files = AsyncPath('.').joinpath('files').glob('*.js')
#     files_queue = asyncio.Queue()
    
#     file_reader = [asyncio.create_task(read_json_file(file, files_queue)) async for file in files]
#     file_writer = asyncio.create_task(write_json_file('data.js', files_queue))
    
#     await asyncio.gather(*file_reader)
#     await files_queue.join()
#     file_writer.cancel()
#     print('Completed')
    
if __name__ == "__main__":
    # STORAGE_DIR = pathlib.Path().joinpath('storage')
    # FILE_STORAGE = STORAGE_DIR / 'data.json'
    
    # if not FILE_STORAGE.exists():
    #     with open(FILE_STORAGE, 'w', encoding='utf-8') as fd:
    #         json.dump([], fd, ensure_ascii=False)
    try:
       num = sys.argv[1]
    except ValueError:
        print("Entered count days to get request")     
           
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main(num))