import scrapy
from ..loaders import AutoyoulaLoader
from .xpaths import AUTO_YOULA_CAR_XPATH, AUTO_YOULA_BRAND_XPATH, AUTO_YOULA_PAGE_XPATH


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def _get_follow(self, response, selector, callback, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link.extract(), callback=callback, cb_kwargs=kwargs)

    def parse(self, response):
        yield from self._get_follow(response,
                                    AUTO_YOULA_PAGE_XPATH["brands"],
                                    self.brand_parse
                                    )

    def brand_parse(self, response):
        callback = {"pagination": self.brand_parse, "car": self.car_parse}
        for key, xpath in AUTO_YOULA_BRAND_XPATH.items():
            yield from self._get_follow(response, xpath, callback[key])

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in AUTO_YOULA_CAR_XPATH.items():
            loader.add_xpath(key, **xpath)
        yield loader.load_item()
