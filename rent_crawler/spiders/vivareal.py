import scrapy
from typing import Union

from datetime import datetime
from rent_crawler.spiders import type2utype

from rent_crawler.items import AddressLoader, SalePropertyLoader, PricesLoader, DetailsLoader, TextDetailsLoader
from rent_crawler.items import VRZapSaleProperty, VRZapAddress, IptuCondoPrices, VRZapDetails, VRZapTextDetails



class VivaRealSpider(scrapy.Spider):
    api_base = 'https://glue-api.vivareal.com//v2/listings'
    total = 10000
    size = 100
    offset = 0
    name = 'vivareal_sale'
    start_url = 'https://glue-api.vivareal.com/v2/listings?'\
                    'addressCity=S%C3%A3o%20Jos%C3%A9%20dos%20Campos'\
                    '&addressLocationId=BR%3ESao%20Paulo%3ENULL%3ESao%20Jose%20dos%20Campos'\
                    '&addressNeighborhood='\
                    '&addressState=S%C3%A3o%20Paulo'\
                    '&addressCountry=Brasil'\
                    '&addressStreet='\
                    '&addressZone='\
                    '&addressPointLat=-23.21984'\
                    '&addressPointLon=-45.891566'\
                    '&business=SALE'\
                    '&facets=amenities'\
                    '&unitTypes='\
                    '&unitSubTypes='\
                    '&unitTypesV3='\
                    '&usageTypes='\
                    '&listingType=USED'\
                    '&parentId=null'\
                    '&categoryPage=RESULT'\
                    '&includeFields=search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount)%2Cpage%2CseasonalCampaigns%2CfullUriFragments%2Cnearby(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Cexpansion(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier%2Cphones)%2Cfacets%2Cdevelopments(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Cowners(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))'\
                    '&size={size}'\
                    '&from={offset}'\
                    '&q='\
                    '&developmentsSize=5'\
                    '&__vt=grid'\
                    '&levels=CITY'\
                    '&ref='\
                    '&pointRadius='\
                    '&isPOIQuery='
    # url_sjc_t = 'https://www.vivareal.com.br/venda/sp/sao-jose-dos-campos/?pagina={page}#onde=,S%C3%A3o%20Paulo,S%C3%A3o%20Jos%C3%A9%20dos%20Campos,,,,,city,BR%3ESao%20Paulo%3ENULL%3ESao%20Jose%20dos%20Campos,,,'
    
    headers = {
        'x-domain': 'www.vivareal.com.br',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0'
    }

    def start_requests(self):
        while self.offset + self.size <= self.total:
            self.logger.info(f"going from {self.offset} ---> {self.offset + self.size}, with a total of {self.total}")
            req_url = self.start_url.format(offset = self.offset, size = self.size)
            yield scrapy.Request(url=req_url, headers=self.headers)
            self.offset += self.size

    def parse(self, response, **kwargs) -> VRZapSaleProperty:
        json_response = response.json()
        # self.logger.info(json_response)
        self.total = json_response['search']['totalCount'] if json_response['search']['totalCount'] <= 10000 else 10000
        for result in json_response['search']['result']['listings']:
            data = result['listing']
            loader = SalePropertyLoader(item=VRZapSaleProperty())
            if data.get('pricingInfos')[0]['businessType'] == 'SALE':
              loader.add_value('kind', 'Sale')
            else:
              loader.add_value('kind','Rent')
            loader.add_value('code', f"VR_{data['id']}")
            loader.add_value('address', self.get_address(data['address']))
            loader.add_value('prices', self.get_prices(data['pricingInfos']))
            loader.add_value('details', self.get_details(data))
            loader.add_value('text_details', self.get_text_details(data))
            loader.add_value('url', self.get_site_url())
            loader.add_value('url', result['link']['href'])
            yield loader.load_item()

    @classmethod
    def get_address(cls, json_address: dict) -> VRZapAddress:
        address_loader = AddressLoader(item=VRZapAddress())
        address_loader.add_value('rua', json_address.get('street'))
        # streetNumber = cls.get_item()
        address_loader.add_value('rua', json_address.get('streetNumber'))
        address_loader.add_value('bairro', json_address.get('neighborhood'))
        address_loader.add_value('cidade', json_address.get('city'))
        address_loader.add_value('estado', json_address.get('stateAcronym'))
        address_loader.add_value('location', json_address.get('point'))
        # address_loader.add_value('lat', json_address['point'].get('lat'))
        # address_loader.add_value('lng', json_address['point'].get('lon'))
        address_loader.add_value('cep', json_address.get('zipCode'))
        address_loader.add_value('zone', json_address.get('zone'))
        yield address_loader.load_item()

    @classmethod
    def get_prices(cls, json_price: dict) -> IptuCondoPrices:
        prices_loader = PricesLoader(item=IptuCondoPrices())
        price_dict = json_price[0] if isinstance(json_price, list) else json_price
        prices_loader.add_value('price', price_dict.get('price'))
        prices_loader.add_value('updated', datetime.now().timestamp())
        prices_loader.add_value('iptu', price_dict.get('yearlyIptu'))
        prices_loader.add_value('condo', price_dict.get('monthlyCondoFee'))
        yield prices_loader.load_item()

    @classmethod
    def get_details(cls, json_details: dict) -> VRZapDetails:
        details_loader = DetailsLoader(item=VRZapDetails())
        totalAreas = cls.get_item(json_details.get('totalAreas'))
        details_loader.add_value('size', totalAreas)
        usableAreas = cls.get_item(json_details.get('usableAreas'))
        details_loader.add_value('size', usableAreas)
        bedrooms = cls.get_item(json_details.get('bedrooms'))
        details_loader.add_value('rooms', bedrooms)
        parkingSpaces = cls.get_item(json_details.get('parkingSpaces'))
        details_loader.add_value('garages', parkingSpaces)
        suites = cls.get_item(json_details.get('suites'))
        details_loader.add_value('suites', suites)
        bathrooms = cls.get_item(json_details.get('bathrooms'))
        details_loader.add_value('bathrooms', bathrooms)
        unitTypes = cls.get_item(json_details.get('unitTypes'))
        details_loader.add_value('utype', type2utype(unitTypes) )
        yield details_loader.load_item()

    @classmethod
    def get_text_details(cls, json_listing: dict) -> VRZapTextDetails:
        text_details_loader = TextDetailsLoader(item=VRZapTextDetails())
        text_details_loader.add_value('description', json_listing.get('description'))
        # text_details_loader.add_value('characteristics', json_listing.get('amenities'))
        text_details_loader.add_value('title', json_listing.get('title'))
        # text_details_loader.add_value('contact', json_listing.get('advertiserContact').get('phones'))
        text_details_loader.add_value('type', json_listing.get('unitTypes'))
        yield text_details_loader.load_item()

    @classmethod
    def get_item(cls, value: Union[list, None]):
        if isinstance(value, list) and len(value)>0:
            return value[0]
        else:
            return 0
        
        

    def get_site_url(self):
        return 'https://vivareal.com.br'
