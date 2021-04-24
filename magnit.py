from urllib.parse import urljoin
import datetime as dt
import requests
import bs4
import pymongo


class MagnitParse:
    month_mapper = {
        "апреля": 4,
        "мая": 5,
        "января": 1,
        "декабря": 12,
        "июня": 6
    }

    def __init__(self, start_url, db_client):
        self.db = db_client["data_mining"]
        self.start_url = start_url

    def _get_response(self, url):
        response = requests.get(url)
        return response

    def _template(self):
        return {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__header"}).text,
            "title": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda a: a.find("div", attrs={"class": "label__price_old"}
                                          ).text.strip().replace("\n", "."),
            "new_price": lambda a: a.find("div", attrs={"class": "label__price_new"}
                                          ).text.strip().replace("\n", "."),
            "from_date": lambda a: self.__get_date(a.find("div", attrs={"class": "card-sale__date"}
                                                          ).text.strip().split("\n"))[0],
            "to_date": lambda a: self.__get_date(a.find("div", attrs={"class": "card-sale__date"}
                                                        ).text.strip().split("\n"))[-1]
        }

    def _get_soup(self, url):
        response = self._get_response(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_a in catalog.find_all("a", recursive=False):
            product_a = self._parse(product_a)
            self.save(product_a)

    def _parse(self, product_a: bs4.Tag) -> dict:
        product_data = {}
        for key, funk in self._template().items():
            try:
                product_data[key] = funk(product_a)
            except AttributeError:
                pass
        return product_data

    def __get_date(self, data):
        result = []
        for date in data:
            date = date.split()
            date[-1] = self.month_mapper[date[-1]]
            result.append(dt.datetime(year=dt.datetime.now().year, day=int(date[1]), month=date[-1]))
        return result

    def save(self, product_data):
        collection = self.db["magnit"]
        collection.insert_one(product_data)


if __name__ == '__main__':
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient()
    parser = MagnitParse(url, db_client)
    parser.run()
