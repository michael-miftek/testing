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
#70k inserts for each item (4 items total)
for t in range(70000):
    startloop = time.time()
    _ = mydb.adc_peak.insert_one({f'{t}' : f'{points['adc_peak']}'})    
    _ = mydb.adc_area.insert_one({f'{t}' : f'{points['adc_area']}'})    
    _ = mydb.adc_width.insert_one({f'{t}' : f'{points['adc_width']}'})    
    _ = mydb.photon_total.insert_one({f'{t}' : f'{points['count_total']}'})    
    endloop = time.time()
    timearr.append(endloop-startloop)
end = time.time()
print(f"time elapsed for four insert_one at {t} events: {end - start}")
print(f"mean time: {tmean(timearr)}")
print(f"var time: {variation(timearr)}")

peak.drop_indexes()
area.drop_indexes()
width.drop_indexes()
cttot.drop_indexes()

#4 inserts of 70k items
start=time.time()
_ = mydb.adc_peak.insert_many({f'{t}' : f'{points['adc_peak']}'} for t in range(70000))    
_ = mydb.adc_area.insert_many({f'{t}' : f'{points['adc_area']}'} for t in range(70000))    
_ = mydb.adc_width.insert_many({f'{t}' : f'{points['adc_width']}'} for t in range(70000))    
_ = mydb.photon_total.insert_many({f'{t}' : f'{points['count_total']}'} for t in range(70000))    
end=time.time()
print(f"time elapsed for four insert_many at {t} events: {end - start}")

peak.drop_indexes()
area.drop_indexes()
width.drop_indexes()
cttot.drop_indexes()

#1 insert of 280k items
start=time.time()
_ = mydb.adc_peak.insert_many({f'{t}' : f'{points['adc_peak']}'} for t in range(280000))    
end=time.time()
print(f"time elapsed for four insert_many at {t} events: {end - start}")

# x = mycol.insert_one({ "name": "John", "address": "Highway 37" })
# print(x.inserted_id)

# x = mycol.insert_one({ "name": "John", "address": "Highway 37" })
# print(x.inserted_id)

# print(mydb.list_collection_names())

# collist = mydb.list_collection_names()
# if "customers" in collist:
#     print("The collection exists.")

# print(f"mean: {tmean(timearr)}")
# print(f"var: {variation(timearr)}")

time.sleep(60)
mydb.drop_collection(peak)
mydb.drop_collection(area)
mydb.drop_collection(width)
mydb.drop_collection(cttot)
myclient.close()