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
    """Process scraped items.

    This method generates a unique hash ID for each item, converts it to JSON, 
    updates the item with the hash ID, and returns the processed item.

    Parameters:
        item (dict): The scraped item to process.
        spider (Spider): The spider that scraped the item.

    Returns:
        dict: The processed item with added hash ID.
    """
    def process_item(self, item, spider):
        """
        Generates a unique hash ID for the given item, converts it to JSON,
        adds the hash ID to the item, and returns the processed item.
        
        This allows each scraped item to have a unique ID that can be used
        for deduplication. The JSON conversion allows the item data to be 
        stored in MongoDB or Elasticsearch.
        """
        item_hash = hashlib.sha1()
        item_dict = ItemAdapter(item).asdict()
        item_json = json.dumps(item_dict, sort_keys=True)
        item_hash.update(item_json.encode('utf-8'))
        item['item_id'] = item_hash.hexdigest()
        return item     

class CorrectKind:
    """
    Corrects the 'kind' field of items based on their price.
    
    If an item with 'kind' == 'Sale' has a price < 100,000, changes 'kind' to 'Rent'. 
    If an item with 'kind' == 'Rent' has a price >= 100,000, changes 'kind' to 'Sale'.
    
    Parameters:
        item (dict): The scraped item to process.
        spider (Spider): The spider that scraped the item.
        
    Returns:
        dict: The processed item with 'kind' corrected if needed.
    """
    def process_item(self, item, spider):
        if item['kind'] == 'Sale' and item['prices']['price'] < 100000:
            item['kind'] = 'Rent'
        elif item['kind'] == 'Rent' and item['prices']['price'] >= 100000:
            item['kind'] = 'Sale'
        return item


class MongoPipeline:
    """MongoPipeline class.

    Handles storing scraped items in a MongoDB database.

    Attributes:
        collection_name: Name of the MongoDB collection to store items in.  
        mongo_uri: MongoDB connection URI.
        mongo_db: Name of the MongoDB database to use.

    Methods:
        __init__: Initialize the pipeline with MongoDB client.
        from_crawler: Create pipeline instance from Crawler.
        open_spider: Initialize MongoDB client and database on spider open.
        close_spider: Close MongoDB client on spider close.  
        process_item: Store scraped item in MongoDB collection.
    """

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
    """RedisDuplicatePipeline class.

    Handles checking for duplicate items in Redis and dropping duplicates.

    Attributes:
        key_prefix: Prefixes to use for item IDs in Redis.

    Methods:
        __init__: Initialize with Redis client.
        from_crawler: Create pipeline instance from Crawler.
        process_item: Check for duplicate item in Redis, drop if found.
    """
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
