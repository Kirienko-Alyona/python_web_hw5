import platform

import aiohttp
import asyncio
import pathlib
import sys
import json
from datetime import datetime

BASE_DIR = pathlib.Path()

async def main(count_days):

    async with aiohttp.ClientSession() as session:       
         
        current_date = datetime.now().date().strftime("%d.%m.%Y")       
       
        # while count_days !=0:
        #     day = day_now
        #     count_days -= 1
        #     date = f"{year_now}.{mon_now}.{day}"
        #     param.append({"Date": date})
        
        try:           
            async with session.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5") as response:
                if response.status == 200:
                    result = await response.json()
                    params = [
                            {
                                current_date: {
                                    result[0]['ccy']: {
                                        "sale": result[0]['sale'], 
                                        "purchase": result[0]['buy']
                                    },
                                    result[1]['ccy']: {
                                        "sale": result[1]['sale'],
                                        "purchase": result[1]['buy']
                                    }
                                }
                            }
                        ]
                    print(params)
                    with open(BASE_DIR.joinpath("storage/data.json"), 'r', encoding='utf-8') as fd:
                        text = fd.readline()
                        if text:
                            upload = json.loads(text)
                    with open(BASE_DIR.joinpath("storage/data.json"), 'w', encoding='utf-8') as fd:                
                        upload.append(params)
                        json.dump(upload, fd, ensure_ascii=False)   
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