# -*- coding: utf-8 -*-
import hashlib
import json
import logging

# import redis as redis
import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
# from scrapyelasticsearch.scrapyelasticsearch import ElasticSearchPipelinekc

logging.getLogger('elasticsearch').setLevel(logging.ERROR)


class RentCrawlerPipeline:
    def process_item(self, item, spider):
        item_hash = hashlib.sha1()
        item_dict = ItemAdapter(item).asdict()
        item_json = json.dumps(item_dict, sort_keys=True)
        item_hash.update(item_json.encode('utf-8'))
        item['item_id'] = item_hash.hexdigest()
        return item
    
class CorrectKind:
    def process_item(self, item, spider):
        if item['kind'] == 'Sale' and item['prices']['price'] < 100000:
            item['kind'] = 'Rent'
        elif item['kind'] == 'Rent' and item['prices']['price'] >= 100000:
            item['kind'] = 'Sale'
        return item


class MongoPipeline:

    collection_name = 'houses'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'houses_db')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        # print(f"Inserted item {item['item_id']}")
        return item
    

class RedisDuplicatePipeline:
    key_prefix = {
        'vivareal': 'VR',
        'zap': 'ZAP',
        'quintoandar': 'QUINTO',
    }

    def __init__(self, redis_host, redis_port):
        if redis_host is not None:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        redis_host = settings.get('REDIS_HOST')
        redis_port = settings.get('REDIS_PORT', default=6379)
        return cls(redis_host, redis_port)

    def process_item(self, item, spider):
        if self.redis_client is None:
            return item

        if 'item_id' in item:
            redis_id = f"{self.key_prefix[spider.name]}:{item['item_id']}"
            existing_id = self.redis_client.get(redis_id)
            if existing_id is not None:
                raise DropItem('Duplicate item found')
            self.redis_client.set(redis_id, 'SEEN')

        return item


# class ElasticSearchAdapterPipeline(ElasticSearchPipeline):
#     def process_item(self, item, spider):
#         item = ItemAdapter(item).asdict()
#         return super().process_item(item, spider)
