import pymongo


db_client = pymongo.MongoClient()
db = db_client["data_mining"]
collection = db["magnit"]

for itm in collection.find():
    print(itm)