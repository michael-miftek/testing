import pymongo
import csv

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
collection = db["your_collection_name"]

# Get the data from the collection
cursor = collection.find()

# Specify the fields you want to export
fields = ["field1", "field2", "field3"]

# Write the data to a CSV file
with open("output.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(fields)

    # Write the data rows
    for document in cursor:
        row = [document.get(field) for field in fields]
        writer.writerow(row)

print("Data exported to output.csv")



# import pandas as pd
# from pymongo import MongoClient
# import json

# def mongoimport(csv_path, db_name, coll_name, db_url='localhost', db_port=27000)
#     """ Imports a csv file at path csv_name to a mongo colection
#     returns: count of the documants in the new collection
#     """
#     client = MongoClient(db_url, db_port)
#     db = client[db_name]
#     coll = db[coll_name]
#     data = pd.read_csv(csv_path)
#     payload = json.loads(data.to_json(orient='records'))
#     coll.remove()
#     coll.insert(payload)
#     return coll.count()