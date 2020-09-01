import requests
import logging

from bs4 import BeautifulSoup
from pymongo import MongoClient

from .utils import doubl_delete


def parse_urls(mongo_configs: dict, start_url: str):
    client = MongoClient(mongo_configs["mongo_url"])
    db = client[mongo_configs["db"]]
    collection = db[mongo_configs["collection_urls"]]

    cnt = 1
    while True:

        try:
            page_resp = requests.get(start_url + f"?page={cnt}")
            soup = BeautifulSoup(page_resp.text, "html.parser")

            block_recipes = soup.find_all("div", {"class": "clearfix"})

            mongo_request = []
            for recipe in block_recipes:
                all_urls = recipe.find_all("a")
                for url in all_urls:
                    find_url = url.get("href")
                    if find_url[:8] == "/recepty":
                        mongo_doc = {"url": find_url, "site_url": start_url}
                        mongo_request.append(mongo_doc)
                        mongo_doc = {}
                        break

            collection.insert_many(mongo_request)
            mongo_request = []
            print(f"data from page number {cnt} is parsed")
            cnt += 1

        except Exception as ex:
            logging.error(ex)
            break

    res = doubl_delete(collection)
    print(f"delete {res} doublicate urls")

    list_ids = []
    for doc in collection.find({}):
        list_ids.append(doc["_id"])

    client.close()

    return list_ids
