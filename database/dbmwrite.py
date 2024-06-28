import pymongo
import time

#Must call this every time after a close event
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
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



def enter(total_runs):
    peak_cursor = peak.find()
    #NOTE: This is the idea of how everything will get updated
    start = time.time()

    peak.update_many(
        { },
        {'$set': {'0': peak_cursor[0][f'{0}'] + points['adc_peak']}}, upsert=True
    )
    end = time.time()
    print(f"updating: {end-start}")
    
def initialize():
    _ = mydb.adc_peak.insert_one({f'{t}' : points['adc_peak']})    
    _ = mydb.adc_area.insert_one({f'{t}' : points['adc_area']})    
    _ = mydb.adc_width.insert_one({f'{t}' : points['adc_width']})    
    _ = mydb.photon_total.insert_one({f'{t}' : points['count_total']})
    
def delete():
    peak.delete_many({})
    area.delete_many({})
    width.delete_many({})
    cttot.delete_many({})
    
def drop():
    mydb.drop_collection(peak)
    mydb.drop_collection(area)
    mydb.drop_collection(width)
    mydb.drop_collection(cttot)
    
def close():
    myclient.close()
    
    
if __name__ == "__main__":
    initialize()
    
    while True:
        x = input('Enter the number of events per second you would like to have: ')     
        break
    
    
    drop()
    close()