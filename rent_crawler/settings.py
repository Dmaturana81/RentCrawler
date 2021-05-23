# -*- coding: utf-8 -*-
BOT_NAME = 'rent_crawler'

SPIDER_MODULES = ['rent_crawler.spiders']
NEWSPIDER_MODULE = 'rent_crawler.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 ' \
             'Safari/601.3.9 '

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_DEBUG = True

CONCURRENT_REQUESTS_PER_DOMAIN = 2

TELNETCONSOLE_ENABLED = False
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None
}

ITEM_PIPELINES = {
    'rent_crawler.pipelines.AwsDynamoDbPipeline': 1
}

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
DYNAMODB_PIPELINE_REGION_NAME = 'sa-east-1'
DYNAMODB_PIPELINE_TABLE_NAME = 'vr-items'

# LOG_STDOUT = True
# LOG_FILE = 'spider_log.txt'

# HTTPERROR_ALLOW_ALL = True
