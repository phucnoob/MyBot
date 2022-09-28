import async_property as _async
from .servers import Server


class Manga:
    __slug = str()
    __chapters = []
    __server = Server

    def __init__(self, slug, server) -> None:
        self.__server = server
        self.__slug = slug
        self.__has_data = False

    async def __fetch_data(self):
        data = await self.__server.get_manga_data(self.__slug)
        if data["ok"]:
            self.__chapters = data.pop("chapters", None)
            data.pop("ok", None)
            self.__has_data = True

            return data

    @_async.async_cached_property
    async def info(self):
        return await self.__fetch_data()

    @property
    def name(self):
        return self.info["name"]

    def __str__(self) -> str:
        return self.name

    def get_chapter(self, index):
        if index >= len(self.__chapters) or index < 0:
            return None

        target = self.__chapters[index]
        if target.get("pages") is None:
            target["pages"] = self.__server.get_chapter_pages(target["slug"])

        return Chapter(target, self.__server)

    @property
    def chapters(self):
        if not self.__has_data:
            self.__fetch_data()  # download the data
        for chap in self.__chapters:
            # Iterator + lazyloading
            if chap.get("pages") is None:
                chap["pages"] = self.__server.get_chapter_pages(chap["slug"])

            yield Chapter(chap, self.__server)


class Chapter:
    def __init__(self, init_data, server: Server) -> None:
        self.pages = init_data["pages"]
        self.slug = init_data["slug"]
        self.name = init_data["name"]
        self.__server = server

    @property
    def images(self):
        for page in self.pages:
            if page.get("image") is None:
                page["image"] = self.__server.get_chapter_page_image(page)
            yield page["image"]

    def __str__(self) -> str:
        return self.name
