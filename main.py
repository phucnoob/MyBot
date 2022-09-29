from time import sleep
from manga.servers.nettruyen import Nettruyen
import json

net = Nettruyen()
mangas = net.search("maou e")

ma = mangas[0]
print(ma.info)

chap = ma.get_chapter(0)

for image in chap.images:
    print(image)


# for manga in mangas:
#     print(json.dumps(manga.info, indent=4, ensure_ascii=False))

# net = Nettruyen()
# manga = net.search("something")
# manga.info = -> dict
# manga.chapters = iterators of Chapter -> download
# manga.get_chapter(index)
# manga.latest() -> fetch and return new chaper
# Chapter -> images []
# iterator of images {buffer, mime_type, name}
