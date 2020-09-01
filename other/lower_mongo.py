from pymongo import MongoClient

import hashlib


client = MongoClient()
db = client["prepare_me"]
collection_recipe = db["recipe"]
collection_ids = db["product_id"]


def lower_ing():
    cnt = 0
    for doc in collection_recipe.find({}):
        cnt += 1
        print(cnt)

        try:
            dict_ingr = doc["ingredients"]

            try:
                for key in dict_ingr:
                    dict_ingr[key.lower()] = dict_ingr.pop(key)
            except Exception as rex:
                print(rex)

            dict_update = {"ingredients": dict_ingr}
            collection_ids.find_one_and_update(
                {"_id": doc["_id"]}, {"$set": dict_update}
            )

        except Exception as ex:
            print(ex)


def lower_id():

    dict_ids = {}
    for doc in collection_ids.find({}):
        dict_ids = doc["product_ids"]
        break

    changed_dict = {}
    cnt = 0
    for key in dict_ids:
        cnt += 1
        print(cnt)

        try:
            changed_dict[key.lower().strip()] = dict_ids[key]
        except Exception as rex:
            pass

    dict_update = {"product_ids": changed_dict}
    collection_ids.find_one_and_update({"_id": doc["_id"]}, {"$set": dict_update})


if __name__ == "__main__":
    lower_id()
