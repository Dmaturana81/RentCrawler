import scrapy
from typing import Union

from datetime import datetime, date
from rent_crawler.spiders import type2utype

from rent_crawler.items import AddressLoader, SalePropertyLoader, PricesLoader, DetailsLoader, TextDetailsLoader, ItemLoader
from rent_crawler.items import KogakeTextDetails, KogakeSaleProperty, KogakeAddress, KogakeDetails, KogakeimoveisMediaDetails, KogakePrices


class KogakeSpider(scrapy.Spider):
    api_base = 'https://www.kogake.com.br/api/'
    total = 1000
    size = 12
    offset = 0
    page = 1
    name = 'kogake_sale'
    start_url = 'https://www.kogake.com.br/api/listings/a-venda/sao-jose-dos-campos?pagina={page}'
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'accept-language': 'en-US,es-CL;q=0.7,pt;q=0.3',
        'accept-encoding': 'gzip, deflate, br',
        'dnt': '1',
        'connection': 'keep-alive',
        'referer': 'https://www.kogake.com.br/imoveis/a-venda/sao-jose-dos-campos',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'Sec-Fetch-User':'?1',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'Host' : 'www.kogake.com.br',
        }
    
    # custom_settings = {
    # 'DOWNLOADER_MIDDLEWARES': {
    #     'rent_crawler.middlewares.CustomProxyMiddleware': 350,
    #     },
    # }
    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("LOG_FILE", f'{date.today().strftime("%y_%m_%d")}_KO_spider_log.txt', priority="spider")
        settings.set("AUTOTHROTTLE_TARGET_CONCURRENCY", 0.3, priority="spider")
        settings.set("CONCURRENT_REQUESTS_PER_DOMAIN", 1, priority="spider")
        settings.set("DOWNLOAD_DELAY", 30, priority="spider")
        settings.set("RANDOMIZE_DOWNLOAD_DELAY",True)


    def start_requests(self):
        # scrapy.Request(url='https://www.kogake.com.br/', headers=self.headers)
        while self.offset + self.size <= self.total:
            self.logger.info(f"going from {self.offset} ---> {self.offset + self.size}, with a total of {self.total}")
            req_url = self.start_url.format(page = self.page)
            yield scrapy.Request(url=req_url, headers=self.headers)
            self.offset += self.size
            self.page += 1

    def parse(self, response, **kwargs) -> KogakeSaleProperty:
        json_response = response.json()
        self.total = json_response['count'] if json_response['count'] <= 1000 else 1000
        for json_source in json_response['data']:
            loader = SalePropertyLoader(item=KogakeSaleProperty())
            if json_source.get('sale_price')[0] > 0 :
              loader.add_value('kind', 'Sale')
            else:
              continue
            loader.add_value('code', f"KO_{json_source['property_full_reference']}")
            loader.add_value('address', self.get_address(json_source))
            loader.add_value('prices', self.get_prices(json_source))
            loader.add_value('details', self.get_details(json_source))
            loader.add_value('text_details', self.get_text_details(json_source))
            loader.add_value('media', self.get_media_details(json_source))

            loader.add_value('url', self.get_site_url())
            loader.add_value('url', json_source.get('url'))
            loader.add_value('url','?from=sale')
            yield loader.load_item()

    @classmethod
    def get_address(cls, json_address: dict) -> KogakeAddress:
        address_loader = AddressLoader(item=KogakeAddress())
        address_loader.add_value('bairro', json_address.get('neighborhood'))
        address_loader.add_value('cidade', json_address.get('city'))
        address_loader.add_value('estado', json_address.get('state'))
        yield address_loader.load_item()

    @classmethod
    def get_prices(cls, json_price: dict) -> KogakePrices:
        prices_loader = PricesLoader(item=KogakePrices())
        prices_loader.add_value('price', json_price.get('sale_price'))
        prices_loader.add_value('updated', datetime.now().timestamp())
        iptu = json_price.get('property_tax')
        if iptu:
            iptu = iptu * 10 if json_price.get('property_tax_payment') == 'MONTHLY' else iptu
        else:
            iptu = 0
        prices_loader.add_value('iptu', iptu)
        prices_loader.add_value('condo', json_price.get('condo_fees'))
        yield prices_loader.load_item()

    @classmethod
    def get_details(cls, json_details: dict) -> KogakeDetails:
        details_loader = DetailsLoader(item=KogakeDetails())
        details_loader.add_value('size', json_details.get('area'))
        details_loader.add_value('rooms', json_details.get('bedrooms'))
        details_loader.add_value('garages', json_details.get('garages'))
        details_loader.add_value('suites', json_details.get('suites'))
        details_loader.add_value('bathrooms', json_details.get('bathrooms'))
        unitTypes = json_details.get('property_type')
        details_loader.add_value('utype', type2utype(unitTypes) )
        yield details_loader.load_item()

    @classmethod
    def get_text_details(cls, json_listing: dict) -> KogakeTextDetails:
        text_details_loader = TextDetailsLoader(item=KogakeTextDetails())
        text_details_loader.add_value('description', json_listing.get('listing_description'))
        text_details_loader.add_value('characteristics', json_listing.get('amenities'))
        text_details_loader.add_value('title', json_listing.get('website_title'))
        text_details_loader.add_value('contact', json_listing.get('contacts'))
        text_details_loader.add_value('type', json_listing.get('property_type'))
        yield text_details_loader.load_item()

    @classmethod
    def get_media_details(cls, json_source: dict) -> KogakeimoveisMediaDetails:
        media_details_loader = ItemLoader(item=KogakeimoveisMediaDetails())
        media_details_loader.add_value('images', json_source.get('photos'))
        media_details_loader.add_value('captions', json_source.get('photos'))
        yield media_details_loader.load_item()

    @classmethod
    def get_item(cls, value: Union[list, None]):
        if isinstance(value, list) and len(value)>0:
            return value[0]
        else:
            return 0

    def get_site_url(self):
        return 'https://www.kogake.com.br'
