from pymongo import MongoClient

import json


client = MongoClient()
db = client["prepare_me"]
collection = db["recipe_urls"]

urls = []

for doc in collection.find({}):
    url = doc["url"]
    urls.append(url)

doubl_dict = {}
for url in urls:
    cnt = urls.count(url)
    if url not in doubl_dict and cnt > 1:
        doubl_dict[url] = cnt

print(json.dumps(doubl_dict, indent=4))
