import json
from datetime import datetime, date
import unidecode
import scrapy
from scrapy.loader import ItemLoader

from ast import literal_eval
from rent_crawler.spiders import type2utype
from rent_crawler.items import SalePropertyLoader, AddressLoader, PricesLoader, DetailsLoader, TextDetailsLoader, ItemLoader
from rent_crawler.items import TopSaleProperty, TopAddress, Prices, EmCasaDetails, TextDetails, TopimoveisMediaDetails


class Topimoveis(scrapy.Spider):
    name = 'topimoveis_sale'
    base_url = 'https://www.topimoveissjc.com.br'
    api_url = f"{base_url}/api/service/consult"

    post_data = '''{{
        "start":{offset},
        "numRows":{size},
        "type":"S",
        "place":null,
        "idtCityList":[1],
        "idtDistrictList":[],
        "idtCondominiumList":[],
        "idtsCategories":[],
        "idtsSubCategories":[],
        "mapSubCategories":{{}},
        "rooms":null,
        "bathrooms":null,
        "garages":null,
        "characteristics":[],
        "condominiumCharacteristics":[],
        "fromPrice":null,
        "toPrice":null,
        "minArea":null,
        "maxArea":null,
        "usefulArea":false,
        "namStreet":null,
        "searchTotal":false,
        "flgRentByPeriod":false,
        "idtsCampaigns":[],
        "getAccess":true,
        "post":true,
        "sortList":["code_DESC"],
        "fieldList":
                    [
                "indType","jsonPhotos","namCategory","namCity","idtCity","namCondominium","namDistrict","namState",
                "namStreet","namSubCategory","numNumber","prop_char_1","prop_char_2","prop_char_95","prop_char_5",
                "prop_char_176","prop_char_12","totalGarages","totalRooms","valLocation","valSales","idtProperty",
                "latitude","longitude","totalAccess","jsonCampaigns","flgHighlight","jsonOffers","idtExternal",
                "flgReservedLocation"
                ],
        "jsonPhotosNum":5,
        "hidePendingLocation":false,
        "hidePrevisionOutput":false,
        "hideApprovedDocumentation":false
        }} '''
    
    headers = {
        'Host': 'www.topimoveissjc.com.br',
        'User-Agent':' Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,es-CL;q=0.7,pt;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin':'https://www.topimoveissjc.com.br',
        'DNT': 1,
        'Connection': 'keep-alive',
        # 'Referer': 'https://www.topimoveissjc.com.br/alugar/sao-jose-dos-campos-sp',
        'Cookie': 'cookieMold=true',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers'
    }

    custom_settings = {
        'ELASTICSEARCH_INDEX': 'rent-quintoandar'
    }

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("LOG_FILE", f'{date.today().strftime("%y_%m_%d")}_TIs_spider_log.txt', priority="spider")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total = 100
        self.size = 6
        self.offset = 0

    def start_requests(self):
        while self.offset < self.total:
            self.logger.info(f"going from {self.offset} ---> {self.offset + self.size}, with a total of {self.total}")
            json_data = json.dumps(json.loads(self.post_data.format( offset=self.offset, size=self.size)))
            yield scrapy.Request(url=self.api_url, method='POST', headers=self.headers, body=json_data)
            self.offset += self.size

    def parse(self, response, **kwargs) -> TopSaleProperty:
        json_response = response.json()
        self.total = json_response['response']['numFound']
        for result in json_response['response']['docs']:
            loader = SalePropertyLoader(item=TopSaleProperty())
            loader.add_value('kind', 'Sale')
            loader.add_value('code', f"TI_{result['idtProperty']}")
            loader.add_value('address', self.get_address(result))
            loader.add_value('prices', self.get_prices(result))
            loader.add_value('details', self.get_details(result))
            loader.add_value('text_details', self.get_text_details(result))
            loader.add_value('media', self.get_media_details(result))
            loader.add_value('url', self.get_site_url(result))
            loader.add_value('url', str(result['idtProperty']))
            yield loader.load_item()

    @classmethod
    def get_address(cls, json_source: dict) -> TopAddress:
        address_loader = AddressLoader(item=TopAddress())
        address_loader.add_value('rua', json_source.get('namStreet'))
        address_loader.add_value('rua', json_source.get('numNumber'))
        address_loader.add_value('bairro', json_source.get('namDistrict'))
        address_loader.add_value('cidade', json_source.get('namCity'))
        address_loader.add_value('estado', json_source.get('namState'))
        address_loader.add_value('name', json_source.get('namCondominium'))
        location = [json_source.get('latitude'), json_source.get('longitude')]
        if len([x for x in location if x]) >0:
            address_loader.add_value('location', location)
        yield address_loader.load_item()


    @classmethod
    def get_prices(cls, json_source: dict) -> Prices:
        prices_loader = PricesLoader(item=Prices())
        prices_loader.add_value('price', json_source.get('valSales'))
        prices_loader.add_value('updated', datetime.now().timestamp())
        yield prices_loader.load_item()

    @classmethod
    def get_details(cls, json_source: dict) -> EmCasaDetails:
        details_loader = DetailsLoader(item=EmCasaDetails())
        details_loader.add_value('size', json_source.get('prop_char_95'))
        details_loader.add_value('rooms', json_source.get('prop_char_5'))
        details_loader.add_value('garages', json_source.get('totalGarages'))
        details_loader.add_value('bathrooms',json_source.get('prop_char_176'))
        details_loader.add_value('utype', type2utype(json_source.get('namCategory')))
        yield details_loader.load_item()

    @classmethod
    def get_site_url(cls, address):
        type = unidecode.unidecode(address.get('namCategory'))
        if type:
            type = type.replace(' ','-')
        city = unidecode.unidecode(address.get('namCity'))
        if city:
            city = city.replace(' ','-')
        bairro = unidecode.unidecode(address.get('namDistrict'))
        if bairro:
            bairro = bairro.replace(' ','-')
        condname = unidecode.unidecode(address.get('namCondominium')) if address.get('namCondominium') else None
        if condname:
            condname = unidecode.unidecode(condname.replace(' ','-'))
            bairoo_condo = f"{bairro}-{condname}"
        else:
            bairoo_condo = f"{bairro}"
        # "https://topimoveissjc.com.br/imovel/venda/apartamentos/sao-jose-dos-campos/floradas-de-sao-jose-edificio-esther/1119"
        yield f"https://topimoveissjc.com.br/imovel/venda/{type}/{city}/{bairoo_condo}/"


    @classmethod
    def get_text_details(cls, json_source: dict) -> TextDetails:
        text_details_loader = TextDetailsLoader()
        text_details_loader.add_value('type', json_source.get('namCategory'))
        yield text_details_loader.load_item()

    @classmethod
    def get_media_details(cls, json_source: dict) -> TopimoveisMediaDetails:
        media_details_loader = ItemLoader(item=TopimoveisMediaDetails())
        media_details_loader.add_value('images', literal_eval(json_source.get('jsonPhotos')))
        media_details_loader.add_value('captions', literal_eval(json_source.get('jsonPhotos')))
        yield media_details_loader.load_item()

