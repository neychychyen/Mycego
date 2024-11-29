import requests
import json

#Запакует всю информацию о экземпляре
class YandexInstance:
    def __init__(self, instance):
        self.body = instance

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

    def get_tree(self, path="/"):

        parent = Folder(
            {
                'path': '.',
                'type': 'dir'
            }
        )
        parent.children = self.__get_tree(path)

        return parent

public_key = 'tA8v00ew6x9O0Ezt5vcBbAGeeKuLKAqumvExwymvVEuEcJyxnXQHKguovMHY51hJq/J6bpmRyOJonT3VoXnDag=='

x = YandexDisk(public_key)
data = x.get_tree()

class StructureElem:
    def __init__(self, path, indent):
        self.path = path
        self.indent = indent
def build_structure(data, indent=0, structure=None):
    if structure is None:
        structure = []  # Инициализируем структуру, если не передана

    if hasattr(data, 'type') and data.type == 'dir':
        structure.append(StructureElem(data.path, indent))  # Добавляем текущий элемент
        if data.children:
            for elem in data.children:
                build_structure(elem, indent + 1, structure)  # Рекурсивно вызываем для дочерних элементов
    else:
        structure.append(StructureElem(data.body['name'], indent))  # Добавляем обычный элемент

    return structure

def draw_structure(structure):
    for elem in structure:
        #print(type(elem))
        if type(elem) != YandexInstance:
            print('|' + elem.indent*'-' + elem.path)
        #


root = build_structure(data)

draw_structure(root)