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


#Processor for number values
parse_float_or_int = MapCompose(lambda x: process_float_or_int(x))
sum_numbers = Compose(lambda v: sum(v))
bigger_than_zero = MapCompose(parse_float_or_int, lambda v: v if v > 0 else None)

#Processor for text values
strip = MapCompose(str.strip, replace_tags, lambda text: text if text != '' else None)
to_lower = MapCompose( str.lower)

filter_images = MapCompose(lambda media: media.get('url') if media.get('type') == 'IMAGE' else None)
filter_videos = MapCompose(lambda media: media.get('url') if media.get('type') == 'VIDEO' else None)
filter_images_top = MapCompose(lambda media: media.get('urlPhoto'))

format_quintoandar_image_url = MapCompose(lambda img: "https://www.quintoandar.com.br/img/med/" + img)
fromat_piramide_images = MapCompose(lambda img: img['picture_full'])
format_emcasa_image_url = MapCompose(lambda img: "https://res.cloudinary.com/emcasa/image/upload/" + img['filename'])
format_emcasa_image_tag = MapCompose(lambda img: img['name'])
format_top_images = MapCompose(lambda img: img['urlPhoto'])
format_top_captions = MapCompose(lambda img: img['desPhoto'])

remove_source = MapCompose(lambda location: location if location.pop('source', None) else location)

#ADDRESSES ITEMS
#-------------------------------------------
class Address(Item):
    rua = Field(output_processor=Join(', '))
    bairro = Field(input_processor=to_lower)
    cidade = Field()
    estado = Field()

class VRZapAddress(Address):
    complemento = Field()
    cep = Field()
    zone = Field()
    location = Field(input_processor=remove_source)

class QuintoAndarAddress(Address):
    region = Field()

class EmCasaAddress(Address):
    id = Field()

class TopAddress(Address):
    name = Field()
    location = Field()

class AddressLoader(ItemLoader):
    default_item_class = Address
    default_input_processor = strip
    default_output_processor = TakeFirst()

# PRICES ITEMS
#-------------------------------------------

class Prices(Item):
    price = Field()
    updated = Field()
    total = Field(input_processor=TakeFirst(), output_processor=sum_numbers)

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
    utype = Field()

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

class EmCasaMediaDetails(Item):
    images = Field(output_processor=format_emcasa_image_url)
    captions = Field(output_processor=format_emcasa_image_tag)

class PiramideMediaDetails(Item):
    images = Field(output_processor=fromat_piramide_images)
    video = Field()

class VRZapMediaDetails(Item):
    images = Field(input_processor=filter_images, output_processor=fromat_piramide_images)
    video = Field(input_processor=filter_videos)

class TopimoveisMediaDetails(Item):
    images = Field(output_processor=format_top_images)
    captions = Field(output_processor=format_top_captions)

# PROPERTY ITEMS
#-------------------------------------------

# RENTAL PROPERTIES
#-----------------------------------

class RentalProperty(Item):
    kind = Field(serializer = str)
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
    media = Field(serializer=PiramideMediaDetails)
    url = Field(output_processor=Join(''))

class PiramideRentalProperty(RentalProperty):
    address = Field(serializer=Address)
    prices = Field(serializer=IptuCondoPrices)
    details = Field(serializer=VRZapDetails)
    text_details = Field(serializer=VRZapTextDetails)
    media = Field(serializer=PiramideMediaDetails)
    url = Field(output_processor=Join(''))

class QuintoAndarProperty(RentalProperty):
    address = Field(serializer=QuintoAndarAddress)
    prices = Field(serializer=QuintoAndarPrices)
    media = Field(serializer=QuintoAndarMediaDetails)
    url = Field(output_processor=Join('/'))

class EmCasaRentProperty(RentalProperty):
    address = Field(serializer=EmCasaAddress)
    prices = Field(serializer=Prices)
    details = Field(serializer=EmCasaDetails)
    media = Field(serializer=EmCasaMediaDetails)
    url = Field(output_processor=Join(''))

class TopProperty(RentalProperty):
    address = Field(serializer=TopAddress)
    prices = Field(serializer=Prices)
    details = Field(serializer=EmCasaDetails)
    media = Field(serializer=QuintoAndarMediaDetails)
    url = Field(output_processor=Join(''))

class RentalPropertyLoader(ItemLoader):
    default_item_class = RentalProperty
    default_output_processor = TakeFirst()

# SELL PROPERTIES
#-----------------------------------

class SaleProperty(Item):
    kind = Field(serializer=str)
    code = Field(serializer=str)
    address = Field(serializer=Address)
    prices = Field(serializer=Prices)
    details = Field(serializer=Details)
    text_details = Field(serializer=TextDetails)
    media = Field()
    url = Field()
    item_id = Field()

class VRZapSaleProperty(SaleProperty):
    address = Field(serializer=VRZapAddress)
    prices = Field(serializer=IptuCondoPrices)
    details = Field(serializer=VRZapDetails)
    text_details = Field(serializer=VRZapTextDetails)
    media = Field(serializer=PiramideMediaDetails)
    url = Field(output_processor=Join(''))

class PiramideSaleProperty(SaleProperty):
    address = Field(serializer=Address)
    prices = Field(serializer=IptuCondoPrices)
    details = Field(serializer=VRZapDetails)
    text_details = Field(serializer=VRZapTextDetails)
    media = Field(serializer=PiramideMediaDetails)
    url = Field(output_processor=Join(''))

class TopSaleProperty(SaleProperty):
    address = Field(serializer=TopAddress)
    prices = Field(serializer=Prices)
    details = Field(serializer=EmCasaDetails)
    media = Field(serializer=TopimoveisMediaDetails)
    url = Field(output_processor=Join(''))

class EmCasaSaleProperty(SaleProperty):
    address = Field(serializer=EmCasaAddress)
    prices = Field(serializer=Prices)
    details = Field(serializer=EmCasaDetails)
    media = Field(serializer=EmCasaMediaDetails)
    url = Field(output_processor=Join(''))

class SalePropertyLoader(ItemLoader):
    default_item_class = SaleProperty
    default_output_processor = TakeFirst()