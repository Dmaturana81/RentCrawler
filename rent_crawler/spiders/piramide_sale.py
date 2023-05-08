import scrapy
from typing import Union

from datetime import datetime
from rent_crawler.spiders import type2utype

from rent_crawler.items import AddressLoader, SalePropertyLoader, PricesLoader, DetailsLoader, TextDetailsLoader, ItemLoader
from rent_crawler.items import PiramideSaleProperty, Address, IptuCondoPrices, VRZapDetails, VRZapTextDetails, PiramideMediaDetails



class VivaRealSpider(scrapy.Spider):
    total = 1000
    size = 12
    page = 1
    offset = 0
    name = 'piramide_sale'
    start_url = 'https://www.piramideimoveissjc.com.br/api/listings/a-venda/sao-jose-dos-campos?pagina={page}'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0',
        'accept': '*/*',
        'accept-language': 'en-US,es-CL;q=0.7,pt;q=0.3',
        'accept-encoding': 'gzip, deflate, br',
        'x-requested-with': 'XMLHttpRequest',
        'dnt': '1',
        'connection': 'keep-alive',
        'referer': 'https://www.piramideimoveissjc.com.br/imoveis/a-venda/sao-jose-dos-campos',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'content-type': 'application/json'
        }

    def start_requests(self):
        while self.offset  <= self.total:
            self.logger.info(f"going from {self.offset} ---> {self.offset + self.size}, with a total of {self.total}")
            req_url = self.start_url.format(page = self.page)
            yield scrapy.Request(url=req_url, headers=self.headers)
            self.offset += self.size
            self.page += 1

    def parse(self, response, **kwargs) -> SalePropertyLoader:
        json_response = response.json()
        self.total = json_response['count'] if json_response['count'] <= 10000 else 10000
        for result in json_response['data']:
            loader = SalePropertyLoader(item=PiramideSaleProperty())
            if 'FOR_SALE' in result['property_purposes']:
                kind ='Sale'
                price_key = 'sale_price'
            else:
                continue
            loader.add_value('kind',kind)
            loader.add_value('code', f"PI_{result.get('property_full_reference').split('-')[0]}")
            loader.add_value('address', self.get_address(result))
            loader.add_value('prices', self.get_prices(result, price_key))
            loader.add_value('details', self.get_details(result))
            loader.add_value('text_details', self.get_text_details(result))
            loader.add_value('media', self.get_media_details(result))
            loader.add_value('url', self.get_site_url())
            loader.add_value('url', result.get('url'))
            yield loader.load_item()

    @classmethod
    def get_address(cls, json_address: dict) -> Address:
        address_loader = AddressLoader(item=Address())
        address_loader.add_value('rua', json_address.get('street'))
        address_loader.add_value('bairro', json_address.get('neighborhood'))
        address_loader.add_value('cidade', json_address.get('city'))
        address_loader.add_value('estado', json_address.get('state'))
        yield address_loader.load_item()

    @classmethod
    def get_prices(cls, json_price: dict, price_key:str) -> IptuCondoPrices:
        prices_loader = PricesLoader(item=IptuCondoPrices())
        price_dict = json_price[0] if isinstance(json_price, list) else json_price
        prices_loader.add_value('price', price_dict.get(price_key))
        prices_loader.add_value('updated', datetime.now().timestamp())
        prices_loader.add_value('iptu', price_dict.get('property_tax'))
        prices_loader.add_value('condo', price_dict.get('condo_fees'))
        #Add all values into the total
        yield prices_loader.load_item()

    @classmethod
    def get_details(cls, json_details: dict) -> VRZapDetails:
        details_loader = DetailsLoader(item=VRZapDetails())
        totalAreas = cls.get_item(json_details.get('area'))
        details_loader.add_value('size', totalAreas)

        usableAreas = cls.get_item(json_details.get('usableAreas'))
        details_loader.add_value('size', usableAreas)

        bedrooms = cls.get_item(json_details.get('bedrooms'))
        details_loader.add_value('rooms', bedrooms)
        
        parkingSpaces = cls.get_item(json_details.get('garages'))
        details_loader.add_value('garages', parkingSpaces)
        
        suites = cls.get_item(json_details.get('suites'))
        details_loader.add_value('suites', suites)
        
        bathrooms = cls.get_item(json_details.get('bathrooms'))
        details_loader.add_value('bathrooms', bathrooms)
        
        details_loader.add_value('utype', type2utype(json_details.get('property_type')) )
        yield details_loader.load_item()

    @classmethod
    def get_text_details(cls, json_listing: dict) -> VRZapTextDetails:
        text_details_loader = TextDetailsLoader(item=VRZapTextDetails())
        text_details_loader.add_value('description', json_listing.get('listing_description'))
        text_details_loader.add_value('characteristics', json_listing.get('amenities'))
        text_details_loader.add_value('title', json_listing.get('website_title'))
        text_details_loader.add_value('contact', json_listing.get('contacts'))
        text_details_loader.add_value('type', json_listing.get('property_type'))
        yield text_details_loader.load_item()

    @classmethod
    def get_media_details(cls, json_listing: dict) -> PiramideMediaDetails:
        media_details_loader = ItemLoader(item=PiramideMediaDetails())
        media_details_loader.add_value('images', json_listing.get('photos'))
        media_details_loader.add_value('video', json_listing.get('video_url'))
        yield media_details_loader.load_item()

    @classmethod
    def get_item(cls, value: Union[list, None]):
        if isinstance(value, list) and len(value)>0:
            return value[0]
        else:
            return 0

    def get_site_url(self):
        return 'https://www.piramideimoveissjc.com.br'
