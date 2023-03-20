# -*- coding: utf-8 -*-
from itemloaders import Identity
from scrapy import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join, Compose
from w3lib.html import replace_tags


def process_float_or_int(value):
    try:
        return eval(value)
    except:
        return value


parse_float_or_int = MapCompose(lambda x: process_float_or_int(x))
sum_numbers = Compose(lambda v: sum(v))
strip = MapCompose(str.strip, replace_tags, lambda text: text if text != '' else None)
filter_images = MapCompose(lambda media: media.get('url') if media.get('type') == 'IMAGE' else None)
filter_videos = MapCompose(lambda media: media.get('url') if media.get('type') == 'VIDEO' else None)
format_vrzap_image_url = MapCompose(lambda img: img.format(width=870, height=653, action='fit-in'))
format_quintoandar_image_url = MapCompose(lambda img: "https://www.quintoandar.com.br/img/med/" + img)
remove_source = MapCompose(lambda location: location if location.pop('source', None) else location)
bigger_than_zero = MapCompose(parse_float_or_int, lambda v: v if v > 0 else None)

#ADDRESSES ITEMS
#-------------------------------------------
class Address(Item):
    rua = Field(output_processor=Join(', '))
    bairro = Field()
    cidade = Field()
    estado = Field()
    lat = Field()
    lng = Field()

class VRZapAddress(Address):
    complemento = Field()
    cep = Field()
    zone = Field()
    location = Field(input_processor=remove_source)

class QuintoAndarAddress(Address):
    region = Field()

class EmCasaAddress(Address):
    id = Field()

class AddressLoader(ItemLoader):
    default_item_class = Address
    default_input_processor = strip
    default_output_processor = TakeFirst()

# PRICES ITEMS
#-------------------------------------------

class Prices(Item):
    sell = Field()
    rent = Field()
    updated = Field()
    total = Field(output_processor=sum_numbers)


class IptuCondoPrices(Prices):
    condo = Field()
    iptu = Field()


class QuintoAndarPrices(Prices):
    iptu_and_condo = Field()


class PricesLoader(ItemLoader):
    default_item_class = Prices
    default_input_processor = parse_float_or_int
    default_output_processor = TakeFirst()

# DETAILS ITEMS
#-------------------------------------------

class Details(Item):
    size = Field()
    rooms = Field()
    garages = Field()
    type = Field()

class VRZapDetails(Details):
    size = Field(input_processor=bigger_than_zero)
    suites = Field()
    bathrooms = Field()

class EmCasaDetails(Details):
    size = Field(input_processor=bigger_than_zero)
    suites = Field()
    bathrooms = Field()

class DetailsLoader(ItemLoader):
    default_item_class = Details
    default_input_processor = parse_float_or_int
    default_output_processor = TakeFirst()

# TEXT DETAILS ITEMS
#-------------------------------------------

class TextDetails(Item):
    type = Field()


class VRZapTextDetails(TextDetails):
    description = Field(input_processor=strip)
    characteristics = Field(output_processor=Identity())
    title = Field()
    contact = Field(output_processor=Identity())


class TextDetailsLoader(ItemLoader):
    default_item_class = TextDetails
    default_output_processor = TakeFirst()

# MEDIA ITEMS
#-------------------------------------------

class QuintoAndarMediaDetails(Item):
    images = Field(output_processor=format_quintoandar_image_url)
    captions = Field()


class VRZapMediaDetails(Item):
    images = Field(input_processor=filter_images, output_processor=format_vrzap_image_url)
    video = Field(input_processor=filter_videos)

# PROPERTY ITEMS
#-------------------------------------------

class RentalProperty(Item):
    code = Field(serializer=str)
    address = Field(serializer=Address)
    prices = Field(serializer=Prices)
    details = Field(serializer=Details)
    text_details = Field(serializer=TextDetails)
    media = Field()
    url = Field()
    item_id = Field()


class VRZapRentalProperty(RentalProperty):
    address = Field(serializer=VRZapAddress)
    prices = Field(serializer=IptuCondoPrices)
    details = Field(serializer=VRZapDetails)
    text_details = Field(serializer=VRZapTextDetails)
    media = Field(serializer=VRZapMediaDetails)
    url = Field(output_processor=Join(''))


class QuintoAndarProperty(RentalProperty):
    address = Field(serializer=QuintoAndarAddress)
    prices = Field(serializer=QuintoAndarPrices)
    media = Field(serializer=QuintoAndarMediaDetails)
    url = Field(output_processor=Join('/'))

class EmCasaProperty(RentalProperty):
    address = Field(serializer=EmCasaAddress)
    prices = Field(serializer=Prices)
    details = Field(serializer=EmCasaDetails)
    url = Field(output_processor=Join(''))

class RentalPropertyLoader(ItemLoader):
    default_item_class = RentalProperty
    default_output_processor = TakeFirst()
