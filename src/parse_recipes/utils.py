from pymongo import MongoClient


def norm_text(text: str):
    norm = text.replace("\t", "").replace("\n", "").replace("\r", "")
    norm = norm.lstrip().rstrip()
    return norm


def add_product_id(data: dict, collection):
    products = data["ingredients"].keys()
    doc_ids = None
    for document in collection.find({}):
        doc_ids = document
        break

    products_ids = doc_ids["product_ids"]

    last_id = doc_ids["last_id"]
    for product in products:
        if product.lower().strip() not in products_ids:
            products_ids[product.lower().strip()] = last_id + 1
            last_id += 1

    data_update = {"last_id": last_id, "product_ids": products_ids}
    collection.find_one_and_update({"_id": doc_ids["_id"]}, {"$set": data_update})

    return


def mongo_del(list_id: list, collection):
    cnt_delete = len(list_id)
    for _id in list_id:
        collection.delete_one({"_id": _id})

    return cnt_delete


def doubl_delete(collection):

    dict_urls = {}
    for doc in collection.find({}):

        url = doc["url"]
        if url not in dict_urls:
            dict_urls[url] = [doc["_id"]]

        else:
            url_id = dict_urls[url]
            url_id.append(doc["_id"])

    how_del = 0
    for key in dict_urls:
        if len(dict_urls[key]) > 1:
            to_mongo_delete = dict_urls[key][1:]
            res = mongo_del(to_mongo_delete, collection)

            how_del += res

    return how_del


def divide_to_batches(data: list, count):
    batches = []
    for n in range(0, len(data), count):
        batches.append(data[n : n + count])

    return batches
