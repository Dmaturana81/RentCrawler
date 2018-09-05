# -*- coding: utf-8 -*-
from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Compose, Identity, Join

import re


def get_district(address):
    address_list = address.split(' - ')
    district = address_list[0] if len(address_list) < 3 else address_list[1]
    return district.replace(', São Paulo', '')


def get_street(address):
    address_list = address.split(' - ')
    return '' if len(address_list) < 3 else address_list[0]


parse_district = Compose(TakeFirst(), get_district)
parse_street = Compose(TakeFirst(), get_street)
parse_city = Compose(TakeFirst(), lambda address: address.split(' - ')[-1])
parse_number = Compose(TakeFirst(), lambda string: re.findall('\d+|$', string)[0])
parse_currency = Compose(TakeFirst(), lambda price: price.split('R$ ')[-1].replace('.', ''), float)
parse_code = MapCompose(lambda url: url.split('id-')[-1][:-1])
strip = MapCompose(str.strip)
join = Join(', ')


class Address(Item):
    street = Field()
    district = Field()
    city = Field()


class Details(Item):
    size = Field()
    rooms = Field()
    bathrooms = Field()
    garages = Field()


class ZapDetails(Details):
    suite = Field(Details.fields['bathrooms'])


class Prices(Item):
    rent = Field()
    condo = Field()
    iptu = Field()


class Apartment(Item):
    address = Field(serializer=Address)
    details = Field(serializer=Details)
    prices = Field(serializer=Prices)
    description = Field()
    code = Field()
    img_urls = Field()
    source = Field()


class VivaRealApartment(Apartment):
    characteristics = Field()


class DetailsLoader(ItemLoader):
    default_item_class = Details
    default_output_processor = TakeFirst()


class VivaRealDetailsLoader(DetailsLoader):
    default_output_processor = parse_number


class PricesLoader(ItemLoader):
    default_item_class = Prices
    default_output_processor = parse_currency


class AddressLoader(ItemLoader):
    default_item_class = Address
    default_input_processor = strip
    default_output_processor = TakeFirst()


class VivaRealAddressLoader(AddressLoader):
    street_out = parse_street
    district_out = parse_district
    city_out = parse_city


class ZapAddressLoader(AddressLoader):
    street_out = join


class ApartmentLoader(ItemLoader):
    default_item_class = Apartment
    default_output_processor = TakeFirst()

    description_in = strip
    img_urls_out = Identity()


class VivaRealApartmentLoader(ApartmentLoader):
    default_item_class = VivaRealApartment

    characteristics_out = join
    code_in = parse_code
