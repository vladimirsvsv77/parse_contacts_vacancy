import pymongo
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.hhemails3
hhemails3 = db.hhemails3


def write_to_file(text):
    f = open('hh_emails.csv', 'a')
    f.write(text + '\n')
    f.close()


for i in hhemails3.find():
    if i['email'] is not None:
        write_to_file(str(i['email']) + ';' + str(i['vac']) + ';' + str(i['phone']) + ';' + str(i['empl_name']) + ';' + str(i['city']) + ';' + str(i['vac_href']))