from urllib.parse import urljoin
from typing import Callable
import requests
import bs4
from database.db import Database


class GbBlogParse:
    def __init__(self, start_url, comment_url, database: Database):
        self.db = database
        self.start_url = start_url
        self.comment_url = comment_url
        self.done_urls = set()
        self.tasks = []
        self.comment_list = []

    def _get_response(self, *args, **kwargs):
        while True:
            response = requests.get(*args, **kwargs)
            if response.status_code == 200:
                return response

    def _get_soup(self, url):
        resp = self._get_response(url)
        soup = bs4.BeautifulSoup(resp.text, "lxml")
        return soup

    def __create_task(self, url, callback, tag_list):
        for link in set(urljoin(url, href.attrs.get("href"))
                        for href in tag_list if href.attrs.get("href")):
            if link not in self.done_urls:
                task = self._get_task(link, callback)
                self.done_urls.add(link)
                self.tasks.append(task)

    def _parse_feed(self, url, soup) -> None:
        ul = soup.find("ul", attrs={"class": "gb__pagination"})
        self.__create_task(url,
                           self._parse_feed, ul.find_all("a"))
        self.__create_task(url,
                           self._parse_post,
                           soup.find_all("a", attrs={"class", "post-item__title"}))

    def _parse_post(self, url, soup) -> dict:
        author_name_tag = soup.find("div", attrs={"itemprop": "author"})
        self._get_comments(soup.find("comments").attrs.get("commentable-id"))
        data = {
            "post_data": {
                "url": url,
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "date": soup.find("time", attrs={"class": "text-md"}).attrs.get("datetime"),
                "img": soup.find("div", attrs={"class": "blogpost-content"}).find("img").attrs.get("src")
            },
            "author": {"name": author_name_tag.text,
                       "url": urljoin(url, author_name_tag.parent.attrs.get("href"))
                       },
            "tags": [{"name": a_tag.text, "url": urljoin(url, a_tag.attrs.get("href"))}
                     for a_tag in soup.find_all("a", attrs={"class": "small"})]
        }
        return data

    def _get_comments(self, comment_id):
        params = {
            "commentable_type": "Post",
            "commentable_id": comment_id,
            "order": "desc"
        }
        response = self._get_response(self.comment_url, params=params)
        data = response.json()
        self.comment_list = self._get_comment_list(data)

    def _get_comment_list(self, data):
        result = []
        my_dict = {"comment_id": 0, "text": "", "author_name": ""}
        for elem in data:
            for value in elem.values():
                my_dict["comment_id"] = value["id"]
                my_dict["text"] = value["body"]
                my_dict["author_name"] = value["user"]["full_name"]
                result.append(my_dict)
                if value["children"]:
                    result.extend(self._get_comment_list(value["children"]))
        return result

    def _get_task(self, url, callback: Callable) -> Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def run(self):
        self.tasks.append(self._get_task(self.start_url, self._parse_feed))
        for task in self.tasks:
            result = task()
            if isinstance(result, dict):
                self.db.create_post(result)
                for comment in self.comment_list:
                    self.db.create_comment(comment, result["post_data"]["url"])


if __name__ == '__main__':
    db = Database("sqlite:///gb_blog.db")
    parser = GbBlogParse("https://geekbrains.ru/posts", "https://gb.ru/api/v2/comments", db)
    parser.run()
