import random
import web
from web.template import ALLOWED_AST_NODES
from dataclasses import dataclass
from collections import defaultdict
import os


@dataclass
class Image:
    path: str
    needed_amount_of_shows: int
    # TODO наверное информацию о последнем показе можно просто хранить в сессии, а не каждом экземпляре класса
    shown_last_time: bool = False


# отключить дебаг для того чтобы работали сессии
web.config.debug = False

ALLOWED_AST_NODES.append('Constant')
render = web.template.render('templates/')
urls = (
    '/', 'index'
)
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'data': None, "initiated": False})


# Считывает конфиг в словарь. Ключи - навания категорий, значения - массив экземплров Image. То есть каждой категории
# сопоставляется список всех соответствующих ей изображений
def get_config():
    with open("config.csv") as config:
        data_index = defaultdict(list)
        for line in config:
            data = line.strip().split(";")
            img = Image(data[0], int(data[1]), False)
            for category in data[2:]:
                data_index[category].append(img)
    return data_index


# Для того, чтобы выполнить дополнительные условия задачи, будем среди всех соответствующих запросу изображений
#  искать то, которое не было показано в прошлый раз, и имеющее наибольший остаток показов
# Принимает массив переданных в запросе категорий.
def get_next_pic(categories):
    # TODO отсортировать изображеия по количеству показов чтобы постоянно не искать максимальное?
    matching_categories = set(categories).intersection(session._initializer["data"].keys())
    if not matching_categories:
        return None
    best_value = -1
    best_index = 0
    tmp = 0
    for category in matching_categories:
        if len(session._initializer["data"][category]) == 1 and session._initializer["data"][category][
            0].shown_last_time:
            session._initializer["data"][category][0].shown_last_time = False
            max = 0
        else:
            max = float('-inf')
            for i, image in enumerate(session._initializer["data"][category]):
                if image.shown_last_time:
                    image.shown_last_time = False
                    continue
                if image.needed_amount_of_shows > max:
                    max = image.needed_amount_of_shows
                    tmp = i
        if max > best_value:
            best_category = category
            best_index = tmp
            best_value = max
    image = session._initializer["data"][best_category][best_index]
    image.shown_last_time = True
    image.needed_amount_of_shows -= 1
    if image.needed_amount_of_shows == 0:
        for category in tuple(session._initializer["data"].keys()):
            if image in session._initializer["data"][category]:
                session._initializer["data"][category].remove(image)
                if len(session._initializer["data"][category]) == 0:
                    del (session._initializer["data"][category])
    return image


# непоятно почему не работают нормально сессии как в tutorial. Сделано через _initializer
# https://stackoverflow.com/questions/23148369/web-py-session-does-not-work-at-all
class index:
    def GET(self):
        # Будем хранить информацию об изображениях в сессии
        if not session._initializer.get('data', False) and not session._initializer.get('initiated', False):
            session._initializer["data"] = get_config()
            session._initializer["initiated"] = True
        elif not session._initializer.get('data', False) and session._initializer.get('initiated', True):
            return ("No more images to show")
        categories = web.input(category=[])
        if not categories.category:
            categories.category = random.choices(list(session._initializer["data"].keys()),
                                                 k=random.randint(1, len(session._initializer["data"])))
        pic = get_next_pic(categories.category)
        if not pic:
            return ("No matching images")
        imageBinary = open(os.path.join(r"static", pic.path), 'rb').read()
        return imageBinary


if __name__ == "__main__":
    app.run()
