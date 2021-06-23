import scrapy
from ..loaders import HhLoader
from .xpaths import HH_PAGE_XPATH, HH_VACANCY_XPATH

class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy']

    def _get_follow(self, response, selector, callback, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link.extract(), callback=callback, cb_kwargs=kwargs)

    def parse(self, response):
        callback = {"pagination": self.parse, "vacancy": self._vacancy_parse}
        for key, xpath in HH_PAGE_XPATH.items():
            yield from self._get_follow(response, xpath, callback[key])

    def _vacancy_parse(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in HH_VACANCY_XPATH.items():
            loader.add_xpath(key, **xpath)
        yield loader.load_item()
