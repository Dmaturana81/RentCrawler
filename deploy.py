from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
import pymongo

setting = get_project_settings()
process = CrawlerProcess(setting)
spiderloaders = SpiderLoader(setting)

for spider_name in spiderloaders.list():
    if spider_name == 'zap':
        continue
    print("Running spider %s" % (spider_name))
    # query dvh is custom argument used in your scrapy
    process.crawl(spider_name)

process.start()

client = pymongo.MongoClient(setting['MONGO_URI'])
db = client[setting['MONGODB_DATABASE']]
db.drop_collection('current')
db['tmp'].rename('current')