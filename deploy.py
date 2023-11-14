from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader

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
