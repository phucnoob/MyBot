from abc import ABC, abstractmethod
from typing import Dict
import aiohttp

HEADERS = {
    "Connection": "keep-alive",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"105\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"105\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8"
}


class Server(ABC):
    id = str
    name = str
    base_url = str
    search_url = str
    headers = HEADERS

    def __init__(self) -> None:
        self.session = aiohttp.ClientSession(headers=self.headers)

    @abstractmethod
    async def search(self, term: str):
        pass

    @abstractmethod
    async def get_manga_data(self, slug: str) -> Dict:
        pass

    @abstractmethod
    async def get_chapter_pages(self, slug: str):
        pass

    @abstractmethod
    async def get_chapter_page_image(self, page: dict):
        pass
