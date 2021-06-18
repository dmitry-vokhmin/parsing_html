import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['http://www.zillow.com/san-francisco-ca/']
    _xpaths = {
        "pagination": "//a[contains(@class, 'PaginationButton')]/@href",
        "ads": "//article[@role='presentation']//a[contains(@class, 'list-card-link')]/@href"
    }
    def __init__(self, *args, **kwargs):
        super(ZillowSpider, self).__init__(*args, **kwargs)
        self.browser = webdriver.Firefox(executable_path="D:\Downloads\geckodriver.exe")

    def parse(self, response):
        for url in response.xpath(self._xpaths["pagination"]):
            yield response.follow(url, callback=self.parse)
        for url in response.xpath(self._xpaths["ads"]):
            yield response.follow(url, callback=self.ads_parse)
        print(1)

    def ads_parse(self, response):
        self.browser.get(response.url)
        media_col = self.browser.find_element_by_xpath('//div[@data-media-col="true"]')
        len_photo = len(media_col.find_elements_by_xpath('//picture[contains(@class, "media-stream-photo")]'))
        while True:
            for _ in range(5):
                media_col.send_keys(Keys.PAGE_DOWN)
            photos = media_col.find_elements_by_xpath('//picture[contains(@class, "media-stream-photo")]')
            if len_photo == len(photos):
                break
            len_photo = len(photos)
        print(1)


