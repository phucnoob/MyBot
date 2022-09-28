from typing import Dict, List
from bs4 import BeautifulSoup

from manga.models import Manga

from . import Server
# from models import Chapter


class Nettruyen (Server):
    id = "Nettruyen"
    name = "Net truyện"
    base_url = "https://www.nettruyenme.com/"
    search_url = "https://www.nettruyenme.com/Comic/Services/SuggestSearch.ashx"
    manga_url = base_url + "{}"

    async def get_manga_data(self, slug) -> Dict:
        url = self.format_manga_url(slug)
        res = await self.session.get(url)
        data = {
            "ok": False,
            "url": url,
            "name": None,
            "cover": None,
            "author": None,
            "genres": [],
            "status": None,
            "synopsis": None,
            "chapters": [],
            "server": self.name,
        }

        if not res.ok:
            res.close()
            return data

        html = await res.text()
        soup = BeautifulSoup(html, "html.parser")
        main_div = soup.select_one("#item-detail")
        data["name"] = main_div.select_one("h1").text.strip()
        data["author"] = main_div.select_one(
            ".author p:last-child").text.strip()
        data["status"] = main_div.select_one(
            ".status p:last-child").text.strip()
        data["synopsis"] = main_div.select_one(
            ".detail-content p").text.strip()
        data["cover"] = main_div.select_one(
            ".col-image img").attrs["src"].strip()
        # get absolute url.
        propocol = self.base_url.split("://", maxsplit=1)[0]
        data["cover"] = f"{propocol}:{data['cover']}"

        data["genres"] = [anchor.text for anchor in main_div.select(".kind a")]
        data["ok"] = True

        # Chapters
        for anchor in main_div.select(".chapter a"):
            data["chapters"].append(dict(
                name=anchor.text,
                slug=anchor.attrs["href"].split(
                    self.base_url, maxsplit=2)[-1]
            ))

        res.close()
        return data

    async def get_chapter_pages(self, slug):
        url = self.format_manga_url(slug)
        res = await self.session.get(url)
        if not res.ok:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        image_tags = soup.select("#ctl00_divCenter div.page-chapter img")

        chapter_pages = []
        propocol = self.base_url.split("://", maxsplit=1)[0]
        chapter_pages = [
            dict(
                url=f'{propocol}:{img.attrs["src"]}',
                name=img.attrs["alt"]
            ) for img in image_tags
        ]

        return chapter_pages

    async def get_chapter_page_image(self, page: dict):

        self.session.headers.update({"Referer": self.base_url})
        res = self.session.get(page["url"])

        if not res.ok:
            return None

        if not res.headers.get("Content-Type").startswith("image/"):
            return None

        image = res.content
        name = page["name"]

        return {
            "buffer": image,
            "name": name.split("/")[-1]
        }

    async def search(self, term: str) -> List[Manga]:
        """Search and return list of Manga"""

        content = None
        async with self.session.get(self.search_url, params={"q": term}) as resp:
            content = await resp.text()

        soup = BeautifulSoup(content, "html.parser")
        result = []
        for item in soup.select("ul>li a"):
            slug = item.attrs["href"].split(self.base_url)[-1]
            result.append(Manga(slug, self))

        return result

    def format_search_url(self, query):
        pass

    def format_manga_url(self, slug):
        return self.manga_url.format(slug)
