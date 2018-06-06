import requests
import pymongo
from pymongo import MongoClient
import datetime
import time
import argparse


parser = argparse.ArgumentParser(description='start_parsing.py')
parser.add_argument('-d_start')
parser.add_argument('-d_end')
parser.add_argument('-m_start')
parser.add_argument('-m_end')
opt = parser.parse_args()
d_start = int(opt.d_start)
d_end = int(opt.d_end)
m_start = int(opt.m_start)
m_end = int(opt.m_end)


date1 = datetime.date(2018, m_start, d_start)
date2 = datetime.date(2018, m_end, d_end)
day = datetime.timedelta(days=1)


client = MongoClient('localhost', 27017)
db = client.hhemails2
hhemails2 = db.hhemails2


try:
    hhemails2.index_information()['email_1']
except KeyError:
    hhemails2.create_index([("email", pymongo.ASCENDING)], unique=True)


def get_vac_by_day(date):
    count = 0
    url_vac = 'https://api.hh.ru/vacancies?text=менеджер по продажам&per_page=100&'
    for i in range(23):
        start = i
        if len(str(start)) == 1:
            start = '0' + str(start)
        end = i + 1
        if len(str(end)) == 1:
            end = '0' + str(end)
        date_start = date + 'T' + str(start) + ':00:00'
        date_end = date + 'T' + str(end) + ':00:00'
        req = requests.get(url_vac + 'date_from=' + date_start + '&date_to=' + date_end)
        for j in range(req.json()['pages'] + 1):
            page_url = 'https://api.hh.ru/vacancies?text=менеджер по продажам&per_page=100&' + 'page=' + str(j) + '&'
            req = requests.get(page_url + 'date_from=' + date_start + '&date_to=' + date_end)            
            try:
                count += len(req.json()['items'])
                for k in req.json()['items']:
                    vac_id = k['id']
                    try:
                        contants = requests.get('https://api.hh.ru/vacancies/' + str(vac_id)).json()['contacts']
                        phones = contants['phones']
                        email = contants['email']
                        empl = {
                            "qid": str(start),
                            "email": email,
                            "vac": "sales",
                            "phones": phones
                        }
                        hhemails2.insert_one(empl)
                    except:
                        pass
            except:
                print(req.json())


while date1 <= date2:
    print (date1.strftime('%Y-%m-%d'))
    try:
        get_vac_by_day(date1.strftime('%Y-%m-%d'))
    except:
        print('except', date1.strftime('%Y-%m-%d'))
        time.sleep(10)
    date1 = date1 + day
