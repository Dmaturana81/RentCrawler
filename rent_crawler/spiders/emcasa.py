import json
import re
from datetime import datetime, date
import scrapy
from scrapy.loader import ItemLoader

from rent_crawler.spiders import type2utype
from rent_crawler.items import SalePropertyLoader, AddressLoader, PricesLoader, DetailsLoader, TextDetailsLoader
from rent_crawler.items import EmCasaSaleProperty, Address, Prices, EmCasaDetails, EmCasaAddress, TextDetails, EmCasaMediaDetails

re_space = re.compile('\s{2,}')

class EmCasa(scrapy.Spider):
    name = 'emcasa'
    start_url = 'https://api.emcasa.com/graphql_api'
    query = '''"query searchListings($filters: ListingFilterInput, $pagination: ListingSearchPagination, $orderBy: [ListingSearchOrderBy], $isMap: Boolean = false, $collection: String) {\n  searchListings(\n    filters: $filters\n    pagination: $pagination\n    orderBy: $orderBy\n    collection: $collection\n  ) {\n    from\n    totalCount\n    listings @skip(if: $isMap) {\n      ...PartialListing\n      __typename\n    }\n    listings @include(if: $isMap) {\n      ...PartialListingMap\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PartialListing on Listing {\n  id\n  isActive\n  uuid\n  type\n  price\n  area\n  rooms\n  bathrooms\n  floor\n  suites\n  garageSpots\n  insertedAt\n  priceRecentlyReduced\n  normalizedLiquidityRatio\n  previousPrices {\n    price\n    insertedAt\n    __typename\n  }\n  tags {\n    uuid\n    name\n    nameSlug\n    __typename\n  }\n  address {\n    id\n    neighborhood\n    neighborhoodSlug\n    street\n    streetSlug\n    streetNumber\n    city\n    state\n    citySlug\n    stateSlug\n    neighborhoodDescription\n    __typename\n  }\n  images {\n    id\n    filename\n    position\n    __typename\n  }\n  __typename\n}\n\nfragment PartialListingMap on Listing {\n  id\n  price\n  address {\n    id\n    lat\n    lng\n    __typename\n  }\n  __typename\n}"'''
    cquery = csearch = re.sub(re_space,' ',query.replace('\n',''))
    data = '''{{
        "operationName":"searchListings",
        "query": {query},
        "variables":{{
            "isMap":false,
            "pagination":{{
                "from":{offset},
                "size":{size}
            }},
            "filters":{{
                "locationAddress":{{
                    "statesSlug":["sp"],
                    "citiesSlug":["sao-jose-dos-campos"]
                }},
                "types":[],
                "tagsSlug":[],
                "sunPeriods":[],
                "orientations":[]
            }},
            "orderBy":[
                {{
                    "field":"STAT_LISTING_COUNT",
                    "type":"DESC"
                }}
            ]
        }}
    }}'''

    
    headers = {'Content-Type': 'application/json'}
    custom_settings = {
        'ELASTICSEARCH_INDEX': 'rent-quintoandar'
    }

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("LOG_FILE", f'./logs/{date.today().strftime("%y_%m_%d")}_EC_spider_log.txt', priority="spider")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total = 200
        self.size = 10
        self.offset = 0

    def start_requests(self):
        while self.offset < self.total:
            self.logger.info(f"going from {self.offset} ---> {self.offset + self.size}, with a total of {self.total}")
            json_data = json.dumps(json.loads(self.data.format(query = self.cquery, offset=self.offset, size=self.size)))
            yield scrapy.Request(url=self.start_url, method='POST', headers=self.headers, body=json_data)
            self.offset += self.size

    def parse(self, response, **kwargs) -> EmCasaSaleProperty:
        json_response = response.json()
        self.total = json_response['data']['searchListings']['totalCount'] if json_response['data']['searchListings']['totalCount'] <= 10000 else 10000
        for result in json_response['data']['searchListings']['listings']:
            loader = SalePropertyLoader(item=EmCasaSaleProperty())
            loader.add_value('kind', 'Sale')
            loader.add_value('code', f"EC_{result['id']}")
            loader.add_value('address', self.get_address(result['address']))
            loader.add_value('prices', self.get_prices(result))
            loader.add_value('details', self.get_details(result))
            loader.add_value('media', self.get_media_details(result))
            loader.add_value('text_details', self.get_text_details(result))
            loader.add_value('url', self.get_site_url(result['address']))
            loader.add_value('url', result['id'])
            yield loader.load_item()

    @classmethod
    def get_address(cls, json_source: dict) -> Address:
        address_loader = AddressLoader(item=EmCasaAddress())
        address_loader.add_value('rua', json_source.get('street'))
        address_loader.add_value('rua', json_source.get('streetNumber'))
        address_loader.add_value('bairro', json_source.get('neighborhood'))
        address_loader.add_value('cidade', json_source.get('city'))
        address_loader.add_value('estado', json_source.get('state'))
        yield address_loader.load_item()


    @classmethod
    def get_prices(cls, json_source: dict) -> Prices:
        prices_loader = PricesLoader(item=Prices())
        prices_loader.add_value('price', json_source.get('price'))
        prices_loader.add_value('updated', datetime.now().timestamp())
        yield prices_loader.load_item()

    @classmethod
    def get_details(cls, json_source: dict) -> EmCasaDetails:
        details_loader = DetailsLoader(item=EmCasaDetails())
        details_loader.add_value('size', json_source.get('area'))
        details_loader.add_value('rooms', json_source.get('rooms'))
        details_loader.add_value('garages', json_source.get('garageSpots'))
        details_loader.add_value('suites', json_source.get('suites'))
        details_loader.add_value('utype', type2utype(json_source.get('type')))
        yield details_loader.load_item()

    @classmethod
    def get_site_url(cls, address):
        streetSlug = address['streetSlug']
        bairroSlug = address['neighborhoodSlug']
        citySlug = address['citySlug']
        stateSlug = address['stateSlug']
        yield f"https://emcasa.com/imoveis/{stateSlug}/{citySlug}/{bairroSlug}/{streetSlug}/id-"

    @classmethod
    def get_text_details(cls, json_source: dict) -> TextDetails:
        text_details_loader = TextDetailsLoader()
        text_details_loader.add_value('type', json_source.get('type'))
        yield text_details_loader.load_item()

    @classmethod
    def get_media_details(cls, json_source: dict) -> EmCasaMediaDetails:
        media_details_loader = ItemLoader(item=EmCasaMediaDetails())
        media_details_loader.add_value('images', json_source.get('images'))
        media_details_loader.add_value('captions', json_source.get('tags'))
        yield media_details_loader.load_item()

