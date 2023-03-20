import scrapy

from bs4 import BeautifulSoup

from rent_crawler.items import AddressLoader, SellPropertyLoader
from rent_crawler.items import VRZapSellProperty, Address

PAGE_SIZE = 36


class VivaRealSpider(scrapy.Spider):
    api_base = 'https://glue-api.vivareal.com//v2/listings'

    name = 'vivareal'
    start_url = '''https://glue-api.vivareal.com/v2/listings?addressCity=S%C3%A3o%20Jos%C3%A9%20dos%20Campos&addressLocationId=BR%3ESao%20Paulo%3ENULL%3ESao%20Jose%20dos%20Campos&addressNeighborhood=&addressState=S%C3%A3o%20Paulo&addressCountry=Brasil&addressStreet=&addressZone=&addressPointLat=-23.21984&addressPointLon=-45.891566&business=SALE&facets=amenities&unitTypes=&unitSubTypes=&unitTypesV3=&usageTypes=&listingType=USED&parentId=null&categoryPage=RESULT&includeFields=search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount)%2Cpage%2CseasonalCampaigns%2CfullUriFragments%2Cnearby(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Cexpansion(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier%2Cphones)%2Cfacets%2Cdevelopments(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Cowners(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Ctier)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))&size=36&from=&q=&developmentsSize=5&__vt=grid&levels=CITY&ref=&pointRadius=&isPOIQuery='''
    # url_sjc_t = 'https://www.vivareal.com.br/venda/sp/sao-jose-dos-campos/?pagina={page}#onde=,S%C3%A3o%20Paulo,S%C3%A3o%20Jos%C3%A9%20dos%20Campos,,,,,city,BR%3ESao%20Paulo%3ENULL%3ESao%20Jose%20dos%20Campos,,,'
    
    headers = {
        'x-domain': 'www.vivareal.com.br',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0'
    }

    def start_requests(self):
        page = self.start_page
        while page <= self.total//36:
            req_url = self.start_url.format(page = page)
            yield scrapy.Request(url=req_url, headers=self.headers)
            page += 1

    def parse(self, response, **kwargs) -> VRZapSellProperty:
        json_response = response.json()
        # self.logger.info(json_response)
        self.total = json_response['search']['totalCount']
        for result in json_response['search']['result']['listings']:
            data = result['listing']
            loader = SellPropertyLoader(item=VRZapSellProperty)
            loader.add_value('code', f"VR_{data['id']}")
            loader.add_value('address', self.get_address(data['address']))
            loader.add_value('prices', self.get_prices(data['pricingInfos']))
            loader.add_value('details', self.get_details(data['']))
            loader.add_value('text_details', self.get_text_details(data['description']))
            loader.add_value('media', self.get_media_details(result['medias']))
            loader.add_value('url', self.get_site_url())
            loader.add_value('url', result['link']['href'])
            yield loader.load_item()

    @classmethod
    def get_address(cls, text: str) -> Address:
        address = card.find('span',attrs={'class':'property-card__address'}).text.strip(' \n')
        rua = 
        bairro = 
        cidade =
        estado = 
        address_loader = AddressLoader(item=Address())
        address_loader.add_value('rua', rua)
        address_loader.add_value('bairro', bairro)
        address_loader.add_value('cidade', cidade)
        address_loader.add_value('estado', estado)
        return address_loader.load_item()

    def get_site_url(self):
        return 'https://vivareal.com.br'
