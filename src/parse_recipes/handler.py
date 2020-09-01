from pymongo import MongoClient

from logging import StreamHandler
from multiprocessing import Process

from .parse_urls import parse_urls
from .parse_data import parse_data
from .utils import divide_to_batches

start_url = "https://eda.ru/recepty"


def handler(configs: dict):

    data = parse_urls(configs, start_url)

    batches = divide_to_batches(data, 100)
    for batch in batches:
        proc = Process(target=parse_data, args=(configs, mongo_ids_url))

