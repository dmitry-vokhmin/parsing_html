import json
import scrapy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tag_url = "/explore/tags/"

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={
                    "username": self.login,
                    "enc_password": self.password
                },
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]}
            )
        except AttributeError as e:
            if response.json()["authenticated"]:
                for tag in self.tags:
                    yield response.follow(f"{self._tag_url}{tag}/", callback=self._tag_page_parse)

    def _tag_page_parse(self, response):
        pagination = {}
        data = self.js_data_extract(response)
        pagination["next_max_id"] = data["entry_data"]["TagPage"][0]["data"]["recent"]["next_max_id"]
        pagination["next_page"] = str(data["entry_data"]["TagPage"][0]["data"]["recent"]["next_page"])
        if data["entry_data"]["TagPage"][0]["data"]["recent"]["next_media_ids"]:
            pagination["next_media_ids"] = [
                str(itm) for itm in data["entry_data"]["TagPage"][0]["data"]["recent"]["next_media_ids"]
            ]
        pagination["tab"] = "recent"
        pagination["surface"] = "grid"
        pagination["include_persistent"] = "0"
        yield scrapy.FormRequest(
            "https://i.instagram.com/api/v1/tags/python/sections/",
            method="POST",
            callback=self.some,
            formdata=pagination,
            headers={"X-CSRFToken": data["config"]["csrf_token"]},
            dont_filter=True
        )

    def some(self, response):
        print(1)

    def js_data_extract(self, response):
        script = response.xpath("//script[contains(text(), 'window._sharedData =')]/text()").extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])
