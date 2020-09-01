import requests

import logging
import hashlib
import json
import os

from bs4 import BeautifulSoup
from pymongo import MongoClient

from .utils import norm_text, add_product_id


def parse_data(mongo_configs: dict, mongo_ids_url: list):
    client = MongoClient(mongo_configs["mongo_url"])
    db = client[mongo_configs["db"]]
    collection_urls = db[mongo_configs["collection_urls"]]
    collection_recipes = db[mongo_configs["collection_recipes"]]
    proc = os.getpid()

    for url_id in mongo_ids_url:

        base_site_url = None
        mongo_request = []
        count_data_parse = 0
        print(f"\n--start main data parse--{proc}--\n")
        for url in collection_urls.find({"_id": url_id}):
            try:
                count_data_parse += 1
                print(f"{count_data_parse} - {url['url']} - {proc}")

                correct_url = f"https://eda.ru{url['url']}"
                mongo_id = hashlib.sha256(correct_url.encode("utf-8")).hexdigest()

                if base_site_url != url["site_url"]:
                    base_site_url = url["site_url"]

                exist = collection_recipes.find({"_id": mongo_id})
                if exist == None:
                    logging.warning(f"url {correct_url} is parsed")
                    continue

                page_resp = requests.get(correct_url)
                soup = BeautifulSoup(page_resp.text, "html.parser")

                name_recipe = soup.find("h1", {"class": "recipe__name"})
                name_recipe = norm_text(name_recipe.text)
                ingredients = {}
                block_ingredients = soup.find(
                    "div", {"class": "ingredients-list__content"},
                )
                all_ing = block_ingredients.find_all("p")

                for ever in all_ing:
                    product = ever.get("data-ingredient-object")
                    product = json.loads(product.encode("utf-8"))
                    ingredients[product["name"]] = product["amount"]

                instructions = {}
                block_instructions = soup.find("ul", {"class": "recipe__steps"})
                steps = block_instructions.find_all("li", {"class": "instruction"})

                cnt = 0
                for step in steps:
                    cnt += 1
                    step_instruct = step.find(
                        "span", {"class": "instruction__description"}
                    )
                    step_instruct = step_instruct.text
                    step_instruct = norm_text(step_instruct)[3:]
                    instructions[str(cnt)] = step_instruct

                energy_value = {}
                block_energy = soup.find("ul", {"class": "nutrition__list"})

                try:
                    energy_list = block_energy.find_all("li")
                except Exception as ex:
                    logging.error(ex)
                    continue

                for energy in energy_list:
                    nutrition_name = energy.find("p", {"class": "nutrition__name"}).text
                    nutrition_weight = energy.find(
                        "p", {"class": "nutrition__weight"}
                    ).text
                    nutrition_parcent = energy.find(
                        "p", {"class": "nutrition__percent"}
                    ).text
                    energy_value[nutrition_name] = [nutrition_weight, nutrition_parcent]

                mongo_doc = {
                    "_id": mongo_id,
                    "name_recipe": name_recipe,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "base_site_url": base_site_url,
                    "energy_value": energy_value,
                }
                add_product_id(mongo_doc, db[mongo_configs["collection_product_id"]])
                mongo_request.append(mongo_doc)

            try:
                if len(mongo_request) >= 20:
                    collection_recipes.insert_many(mongo_request)
                    mongo_request = []

            except Exception as ex:
                logging.error(ex)
                mongo_request = []
                continue

        except Exception as ex:
            logging.error(ex)
            continue
        
    if len(mongo_request) != 0:
        collection_recipes.insert_many(mongo_request)

    db.drop_collection(mongo_configs["collection_urls"])
    client.close()

    return

