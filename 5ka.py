from pathlib import Path
import time
import json
import requests


class Parse5ka:
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }

    params = {
        "records_per_page": 20,
        "page": 1,
        "categories": ""
    }

    def __init__(self, start_url: str, products_path: Path):
        self.start_url = start_url
        self.products_path = products_path

    @staticmethod
    def _get_response(*args, **kwargs):
        while True:
            response = requests.get(*args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            product_path = self.products_path.joinpath(f"{product['id']}.json")
            self._save(product, product_path)

    def _parse(self, url):
        params = self.params
        while url:
            response = self._get_response(url, headers=self.headers, params=params)
            if params:
                params = {}
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    @staticmethod
    def _save(data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="UTF-8")


class Parser5kaCategories(Parse5ka):
    def __init__(self, start_url, categories_url, products_path):
        super().__init__(start_url, products_path)
        self.categories_url = categories_url

    def _get_categories(self, url):
        response = self._get_response(url)
        return response.json()

    def run(self):
        for category in self._get_categories(self.categories_url):
            self.params["categories"] = category["parent_group_code"]
            for product in self._parse(self.start_url):
                product_path = self.products_path.joinpath(f"{category['parent_group_name']}.json")
                self._save(product, product_path)

    @staticmethod
    def _save(data, file_path):
        with open(file_path, "a") as file:
            file.write(json.dumps(data))


if __name__ == '__main__':
    start_url = "https://5ka.ru/api/v2/special_offers/"
    categories_url = "https://5ka.ru/api/v2/categories/"
    save_path = Path(__file__).parent.joinpath("products")
    if not save_path.exists():
        save_path.mkdir()
    parser = Parser5kaCategories(start_url, categories_url, save_path)
    parser.run()
