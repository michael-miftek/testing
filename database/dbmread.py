import pymongo
import time

newclient = pymongo.MongoClient("mongodb://localhost:27017/")
# print(newclient.read_preference)
# print(newclient.list_database_names())
# namedb = newclient.list_database_names()[3]
x = newclient.get_database(name='mydatabase')
y = x.get_collection('adc_peak')


start = time.time()

ycursor = y.find()
ylist = ycursor[0][f'{0}']
end = time.time()
print(f"updating: {end-start}")

start = time.time()

print(end-start)
print(f"ylist: {ylist}")
