import requests
import os
import json

#Запакует всю информацию о экземпляре
class YandexInstance:
    def __init__(self, instance):
        self.name = instance['name']
        self.url = instance['file']
        self.mime = instance['mime_type']
        self.md5 = instance['md5']

    def download(self, path = './dw'):

        # Загружаем файл
        response = requests.get(self.url, stream=True)

        # Проверка успешности запроса
        if response.status_code == 200:
            with open(path + '/' + self.name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Файл {self.name} успешно скачан!")
        else:
            print(f"Не удалось скачать файл. Статус код: {response.status_code}")

#Только папка может хранить в себе другие файлы (открыто)
class Folder(YandexInstance):
    def __init__(self, instance):

        self.path = instance['path']
        self.type = instance['type']
        self.children = []

    def append(self, child):
        self.children.append(child)


class YandexDisk:
    public_url = 'https://cloud-api.yandex.net/v1/disk/public/resources'

    def __init__(self, public_key):
        self.public_key = public_key

    #Получает все элементы по адресу, нужен публичный ключ, примет путь к подпапкам, если необходимо (нужно для рекурсии)
    @staticmethod
    def __get_json(url, **params):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()  # Возвращаем JSON-ответ
        else:
            print(f"Ошибка запроса: {response.status_code}")
            return None

    @staticmethod
    def __parse_elem(json_elem, get_tree):

        def process_dir(json_elem):
            return {
                'path': json_elem['path'],
                'type': 'dir'
            }

        type_processors = {
            'dir': process_dir,
        }

        processor = type_processors.get(json_elem['type'])

        if processor:
            folder = Folder(processor(json_elem))
            result = get_tree(folder.path)
            folder.children = result
            return folder  # Вызываем соответствующую функцию
        else:
            return YandexInstance(json_elem)

    @staticmethod
    def __parse_data(json_response, parse_elem, get_tree):
        result = json_response['_embedded']['items']
        result = [parse_elem(item, get_tree) for item in result]

        return result

    def __get_tree(self, path):
        result = self.__get_json(self.public_url, public_key=self.public_key, path=path)
        return self.__parse_data(result, self.__parse_elem, self.__get_tree)

    def get_model(self, path="/"):

        parent = Folder(
            {
                'path': '.',
                'type': 'dir'
            }
        )
        parent.children = self.__get_tree(path)

        return [parent]

    def get_info(self):
        info = self.__get_json(self.public_url, public_key=self.public_key)
        return [info['public_key'], info['public_url']]

    def get_info_for_hashes(self, model, hashes = [], paths = []):

        for elem in model:
            if hasattr(elem, 'children'):
                paths.append(elem.path)

                if elem.children:
                    hashes, paths = self.get_info_for_hashes(elem.children, hashes, paths)
            else:
                hashes.append(elem.md5)

        return hashes, paths

    def download_url(self, model, path='', download_array=[]):

        for elem in model:
            #print(path)
            if hasattr(elem, 'children'):
                if elem.children:
                    download_array = self.download_url(elem.children, elem.path)
            else:
                download_array.append([path, elem])

        return download_array

    def download(self, urls, base_path='./', resp_id = 'response'):  # base_path - путь, в котором будут созданы папки
        # Для каждого элемента в списке
        for folder_path, file in urls:
            full_folder_path = os.path.join(base_path + resp_id + folder_path)  # убираем начальный '/'

            #print(full_folder_path)

            # Создаём все необходимые папки (если они не существуют)
            os.makedirs(full_folder_path,
                        exist_ok=True)  # exist_ok=True предотвращает ошибку, если папка уже существует

            # Допустим, мы хотим создать файл (например, пустой) в каждой папке
            file.download(full_folder_path)

    def start(self):
        model = self.get_model()
        info = self.get_info()
        result = self.download_url(model)
        urls = self.download_url(model)
        self.download(urls)


public_key = 'tA8v00ew6x9O0Ezt5vcBbAGeeKuLKAqumvExwymvVEuEcJyxnXQHKguovMHY51hJq/J6bpmRyOJonT3VoXnDag=='

x = YandexDisk(public_key)
x.start()



# data = model
# print(data[0].children[0].children[0].path)
#
# class StructureElem:
#     def __init__(self, path, indent):
#         self.path = path
#         self.indent = indent
#
# def build_structure(data, indent=0, structure=None):
#     if structure is None:
#         structure = []  # Инициализируем структуру, если не передана
#
#     if hasattr(data, 'type') and data.type == 'dir':
#         structure.append(StructureElem(data.path, indent))  # Добавляем текущий элемент
#         if data.children:
#             for elem in data.children:
#                 build_structure(elem, indent + 1, structure)  # Рекурсивно вызываем для дочерних элементов
#     else:
#         structure.append(StructureElem(data.name, indent))  # Добавляем обычный элемент
#
#     return structure
#
# def draw_structure(structure):
#     for elem in structure:
#         #print(type(elem))
#         if type(elem) != YandexInstance:
#             print('|' + elem.indent*' '*3 + elem.path)
#         #
#
#
# root = build_structure(data[0])
#
# draw_structure(root)


# drs = data.children[3].children
#
# #print(drs[0].body)
#
# for elem in drs:
#     print(f'{elem.name}: {elem.download} (hash: {elem.md5}) mime: {elem.mime}')
#     elem.download()