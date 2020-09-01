from pymongo import MongoClient

import hashlib


client = MongoClient()
db = client["prepare_me"]
collection_recipe = db["recipe"]
collection_ids = db["product_id"]

dict_ids = None
for doc in collection_ids.find({}):
    dict_ids = doc["product_ids"]
    break

cnt = 0
for doc in collection_recipe.find({}):
    cnt += 1
    print(cnt)
    list_ids = []
    ingridients = doc["ingredients"]

    for ingridient in ingridients:
        inid = dict_ids[ingridient.lower().strip()]
        list_ids.append(inid)

    list_ids.sort()
    list_strids = [str(x) for x in list_ids]

    strid = "".join(list_strids)
    hash_ids = hashlib.sha256(strid.encode("utf-8")).hexdigest()

    dict_update = {"id_ingredients": list_ids, "hash_ingredients": hash_ids}
    collection_recipe.find_one_and_update({"_id": doc["_id"]}, {"$set": dict_update})


client.close()
