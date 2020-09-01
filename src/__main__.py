from parse_recipes.handler import handler

mongo_configs = {
    "mongo_url": "127.0.0.1:27017",
    "db": "test",
    "collection_urls": "recipe_urls_edaru",
    "collection_recipes": "recipe",
    #"collection_product_id": "product_id",
}

if __name__ == "__main__":

    handler(mongo_configs)

