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
db = client.hhemails3
hhemails3 = db.hhemails3


try:
    hhemails2.index_information()['email_1']
except KeyError:
    hhemails2.create_index([("email", pymongo.ASCENDING)], unique=True)


professions = 'менеджер по продажам or Sales manager or грузчик or Продавец-консультант or Продавец-консультант or повар or пекарь or Специалист колл центр or официант or водитель or продавец'


def get_vac_by_hour(date_start, date_end, url_vac):
    req = requests.get(url_vac + 'date_from=' + date_start + '&date_to=' + date_end)
    for j in range(req.json()['pages'] + 1):
        page_url = 'https://api.hh.ru/vacancies?text=' + professions + '&per_page=100&' + 'page=' + str(j) + '&'
        req = requests.get(page_url + 'date_from=' + date_start + '&date_to=' + date_end)            
        try:
            for k in req.json()['items']:
                vac_id = k['id']
                try:
                    req = requests.get('https://api.hh.ru/vacancies/' + str(vac_id)).json()
                    email = req['contacts']['email']
                    if email is not None:
                        vac_href = req['alternate_url']
                        try:
                            phones = req['contacts']['phones'][0] 
                            phone = phones['country'] + phones['city'] + phones['number']
                        except:
                            phone = ''
                        try:
                            name = req['contacts']['name']
                        except:
                            name = ''
                        try:
                            city = req['address']['city']
                        except:
                            city = ''
                        try:
                            vac_name =req['name']
                        except:
                            vac_name = ''
                        empl = {
                            "qid": str(vac_id),
                            "email": email,
                            "vac": vac_name,
                            "phone": phone,
                            "empl_name": name,
                            "city": city,
                            "vac_href": vac_href
                        }
                        hhemails3.insert_one(empl)
                except:
                    pass
        except:
            print(req.json())


def get_vac_by_day(date):
    url_vac = 'https://api.hh.ru/vacancies?text=' + professions + '&per_page=100&'
    for i in range(23):
        start = i
        if len(str(start)) == 1:
            start = '0' + str(start)
        end = i + 1
        if len(str(end)) == 1:
            end = '0' + str(end)
        get_vac_by_hour(date + 'T' + str(start) + ':00:00', date + 'T' + str(start) + ':30:00', url_vac)
        get_vac_by_hour(date + 'T' + str(start) + ':30:00', date + 'T' + str(end) + ':00:00', url_vac)

        
while date1 <= date2:
    print (date1.strftime('%Y-%m-%d'))
    try:
        get_vac_by_day(date1.strftime('%Y-%m-%d'))
    except:
        print('except', date1.strftime('%Y-%m-%d'))
        time.sleep(10)
    date1 = date1 + day


def write_to_file(text):
    f = open('hh_emails.txt', 'a')
    f.write(text + '\n')
    f.close()


for i in hhemails3.find():
    if i['email'] is not None:
        write_to_file(i['email'])
