import pymongo
import time
from scipy.stats import tmean, variation

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
# mycol = mydb["customers"]
try:
    peak = mydb.create_collection("adc_peak")
    area = mydb.create_collection("adc_area")
    width = mydb.create_collection("adc_width")
    cttot = mydb.create_collection("photon_total")
except:
    pass
# peak = mydb["adc_peak"]
# area = mydb["adc_area"]
# width = mydb["adc_width"]
# cttot = mydb["photon total"]

points = {
    'adc_peak': [47103.0, 33995.0, 35008.0, 36028.0, 35592.0, 34896.0, 50403.0, 36451.0, 33803.0, 34923.0, 34888.0, 34913.0], 
    'adc_area': [1.2949853832322904, 1.7600154426395034, 1.4558833434363845, 1.4272641537237334, 1.616168024003429, 1.773990085278409, 1.115419803392102, 1.0411269060841692, 1.2650121808810502, 1.4290298944300492, 1.6004416530442513, 1.750695021638818], 
    'adc_width': [84, 4, 7, 8, 5, 4, 28, 193, 12, 7, 5, 4], 
    'count_total': [2739, 9, 202, 0, 0, 0, 0, 0, 0, 0, 0, 0]}

docs = [points for x in range(10)]



# mydict = { "name": "John", "address": "Highway 37" }
# mdict = { "name": "John", "address": "Highway 37" }
timearr =[]
start = time.time()
#70k inserts
# for t in range(500):
#     startloop = time.time()
#     _ = mydb.adc_peak.insert_one({f'{t}' : f'{points['adc_peak']}'})    
#     _ = mydb.adc_area.insert_one({f'{t}' : f'{points['adc_area']}'})    
#     _ = mydb.adc_width.insert_one({f'{t}' : f'{points['adc_width']}'})    
#     _ = mydb.photon_total.insert_one({f'{t}' : f'{points['count_total']}'})    
#     endloop = time.time()
#     timearr.append(endloop-startloop)

# _ = mydb.adc_peak.insert_many({f'{t}' : f'{points['adc_peak']}'} for t in range(70000))    
# _ = mydb.adc_area.insert_many({f'{t}' : f'{points['adc_area']}'} for t in range(3500))    
# _ = mydb.adc_width.insert_many({f'{t}' : f'{points['adc_width']}'} for t in range(3500))    
# _ = mydb.photon_total.insert_many({f'{t}' : f'{points['count_total']}'} for t in range(3500))    
# _ = mydb.adc_peak.bulk_write({f'{t}' : f'{points['adc_peak']}'} for t in range(70000))



# from pymongo import InsertOne, DeleteOne, ReplaceOne
# from pymongo.errors import BulkWriteError

# # docs = [... input documents ]
# requests = []
# for i, doc in enumerate(docs):
#     requests.append({
#        ReplaceOne({"docId": f'{i}'}, doc, True)
#    })

# try:
#     mydb.docs.bulk_write(requests, ordered=False)
# except BulkWriteError as bwe:
#     print(bwe.details)


end = time.time()
# x = mycol.insert_one({ "name": "John", "address": "Highway 37" })
# print(x.inserted_id)

# x = mycol.insert_one({ "name": "John", "address": "Highway 37" })
# print(x.inserted_id)

# print(mydb.list_collection_names())

# collist = mydb.list_collection_names()
# if "customers" in collist:
#     print("The collection exists.")
print(f"time elapsed for 500 events: {end- start}")

# print(f"mean: {tmean(timearr)}")
# print(f"var: {variation(timearr)}")

time.sleep(60)
mydb.drop_collection(peak)
mydb.drop_collection(area)
mydb.drop_collection(width)
mydb.drop_collection(cttot)
myclient.close()