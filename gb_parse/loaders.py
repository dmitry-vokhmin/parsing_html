from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import GbAutoyoulaItem, GbHhItem


def get_characteristics(item):
    selector = Selector(text=item)
    return {
        selector.xpath("//div[contains(@class, 'AdvertSpecs_label')]/text()").extract_first():
            selector.xpath("//div[contains(@class, 'AdvertSpecs_data')]//text()").extract_first()
    }


def get_price(item):
    return int(item[0].replace("\u2009", ""))


class AutoyoulaLoader(ItemLoader):
    default_item_class = GbAutoyoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    description_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
    price_out = get_price
    author_out = TakeFirst()


def get_salary(item):
    return "".join(item)


def get_author_url(item):
    return urljoin("https://hh.ru", item[0])


class HhLoader(ItemLoader):
    default_item_class = GbHhItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = get_salary
    author_in = get_author_url
