AUTO_YOULA_PAGE_XPATH = {"brands": "//div[contains(@class, 'ColumnItemList_item')]/a/@href", }

AUTO_YOULA_BRAND_XPATH = {
    "pagination": "//a[contains(@class, 'Paginator_button')]/@href",
    "car": "//a[contains(@class, 'SerpSnippet_name')]/@href", }

AUTO_YOULA_CAR_XPATH = {
    "title": {"xpath": "//div[contains(@class, 'AdvertCard_advertTitle')]/text()"},
    "price": {"xpath": "//div[contains(@class, 'AdvertCard_price')]/text()"},
    "photo": {"xpath": "//div[contains(@class, 'PhotoGallery_photoWrapper')]//@src"},
    "description": {"xpath": "//div[contains(@class, 'AdvertCard_descriptionInner')]/text()"},
    "characteristics": {"xpath": "//div[contains(@class, 'AdvertSpecs_row')]"},
    "author": {"xpath": "//script[contains(text(), 'window.transitState = decodeURIComponent')]",
               "re": r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar"}}

HH_PAGE_XPATH = {
    "pagination": "//a[@data-qa='pager-page']/@href",
    "vacancy": "//a[@data-qa='vacancy-serp__vacancy-title']/@href"}

HH_VACANCY_XPATH = {
    "title": {"xpath": "//h1[@data-qa='vacancy-title']/text()"},
    "salary": {"xpath": "//span[@data-qa='bloko-header-2']/text()"},
    "description": {"xpath": "//div[@data-qa='vacancy-description']//text()"},
    "skills": {"xpath": "//span[@data-qa='bloko-tag__text']/text()"},
    "author": {"xpath": "//div[@class='vacancy-company-logo']/a/@href"}
}
