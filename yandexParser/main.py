import requests
import os
from typing import List, Dict, Union, Any, Optional, Callable, Tuple


#Запакует всю информацию о экземпляре
class YandexInstance:
    def __init__(self, instance: Dict[str, str]) -> None:
        self.name: str = instance['name']
        self.url: str = instance['file']
        self.mime: str = instance['mime_type']
        self.md5: str = instance['md5']

    def download(self, path: str = './') -> None:

        # Загружаем файл
        response = requests.get(self.url, stream=True)

        # Проверка успешности запроса
        if response.status_code == 200:
            with open(path + '/' + self.name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            #print(f"Файл {self.name} успешно скачан!")
        else:
            pass
            #print(f"Не удалось скачать файл. Статус код: {response.status_code}")

#Только папка может хранить в себе другие файлы (открыто)
class Folder(YandexInstance):
    def __init__(self, instance: Dict[str, str]) -> None:

        self.path: str = instance['path']
        self.type: str = instance['type']
        self.children: List[Union[YandexInstance, 'Folder']] = []

    def append(self, child: Union[YandexInstance, 'Folder']) -> None:
        self.children.append(child)

class Session:
    public_url = 'https://cloud-api.yandex.net/v1/disk/public/resources'

    def __init__(self, public_key:str) -> None:
        self.public_key: str = public_key

    @staticmethod
    def __get_json(url: str, **params: Any) -> Optional[Dict[str, Any]]:
        """
                Статический метод для выполнения GET-запроса и получения JSON-ответа.

                :param url: URL для запроса.
                :param params: Дополнительные параметры для GET-запроса.
                :return: Ответ в формате JSON, если запрос успешен; иначе None.
        """
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()  # Возвращаем JSON-ответ
        else:
            # print(f"Ошибка запроса: {response.status_code}")
            return None

    @staticmethod
    def __parse_elem(json_elem: Dict[str, Any], get_tree: Callable[[str], List[Union[YandexInstance, 'Folder']]]) -> Union[Folder, YandexInstance]:
        """
                Метод для парсинга элемента JSON и создания соответствующего объекта.

                :param json_elem: Элемент JSON, содержащий информацию о папке или файле.
                :param get_tree: Функция, которая получает список дочерних объектов для папки.
                :return: Объект Folder, если элемент является директорией, иначе YandexInstance.
        """

        def process_dir(json_elem: Dict[str, Any]) -> Dict[str, str]:
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
    def __parse_data(json_response: Dict[str, Any],
                     parse_elem: Callable[
                         [Dict[str, Any], Callable[[str], List[Union['YandexInstance', 'Folder']]]], Union[
                             'YandexInstance', 'Folder']],
                     get_tree: Callable[[str], List[Union['YandexInstance', 'Folder']]]
                     ) -> List[Union['YandexInstance', 'Folder']]:

        """
                Метод для парсинга данных из JSON-ответа, обработки каждого элемента и возврата списка объектов.

                :param json_response: Ответ в формате JSON, содержащий ключ '_embedded' с элементами.
                :param parse_elem: Функция, которая парсит каждый элемент и возвращает объект YandexInstance или Folder.
                :param get_tree: Функция для получения дочерних элементов для Folder.
                :return: Список объектов типа YandexInstance или Folder.
        """

        result = json_response['_embedded']['items']
        result = [parse_elem(item, get_tree) for item in result]

        return result

    def __get_tree(self, path: str) -> List[Union['YandexInstance', 'Folder']]:
        """
                Метод для получения данных о дереве элементов по заданному пути.

                :param path: Путь для получения данных.
                :return: Список объектов типа YandexInstance или Folder.
        """
        result = self.__get_json(self.public_url, public_key=self.public_key, path=path)
        return self.__parse_data(result, self.__parse_elem, self.__get_tree)



    @staticmethod
    def __crop_url(url: str) -> Tuple[str, str]:
        """
            # Разделяем url по символу "/"
        :param url: str
        :return: возвращает id пути, тип ссылки (i - один файл, d - директория
        """

        parts = url.split('/')  # Разделяем строку по символу "/"
        return parts[-1], parts[-2]

    def get_info(self) -> Tuple[str, str, str, str]:
        """
                Получает информацию о публичном ключе и публичном URL.

                :return: id пути, public_url, public_key, тип ссылки
        """

        info = self.__get_json(self.public_url, public_key=self.public_key)
        cropped = self.__crop_url(info['public_url'])

        return cropped[0], info['public_url'], info['public_key'], cropped[1]

    def get_model(self, path: str = "/") -> Optional[List['Folder']]:

        """
                Возвращает модель из Folder[элементы YandexInstance или Folder]

                :return: id пути, public_url, public_key, тип ссылки
        """
        info = self.get_info()

        parent = Folder(
            {
                'path': '/',
                'type': 'dir'
            }
        )

        # Если директория
        if info[-1] == 'd':

            parent.children = self.__get_tree(path)
            return [parent]

        # Если файл
        elif info[-1] == 'i':

            result = self.__get_json(self.public_url, public_key=self.public_key)


            parent.children = [YandexInstance(result)]

            return [parent]

        else:
            return None


    def get_info_for_hashes(self, model: List['Folder'], hashes: List[str] = [], paths: List[str] = []) -> Tuple[List[str], List[str]]:

        """
                Рекурсивно собирает хэши всех файлов и записывает пути модели данных, нужно для кеширования.

                :param model: Список объектов, содержащий элементы типа YandexInstance или Folder.
                :param hashes: Список для хранения хэшей (по умолчанию пустой).
                :param paths: Список для хранения путей (по умолчанию пустой).
                :return: Кортеж, содержащий два списка: hashes и paths.
        """
        for elem in model:
            if hasattr(elem, 'children'):
                paths.append(elem.path)

                if elem.children:
                    hashes, paths = self.get_info_for_hashes(elem.children, hashes, paths)
            else:
                hashes.append(elem.md5)

        return hashes, paths

    def download_urls(self,
                     model: List['Folder'],
                     path: str = '/',
                     download_array: List[List[Union[str, 'YandexInstance']]] = []
                     ) -> List[List[Union[str, 'YandexInstance']]]:
        """
                Рекурсивно собирает список для скачивания, включая путь и объект для скачивания.

                :param model: Список объектов, содержащий элементы типа YandexInstance или Folder.
                :param path: Путь для текущего элемента (по умолчанию пустая строка).
                :param download_array: Массив для хранения данных о скачиваемых объектах (по умолчанию пустой список).
                :return: Список из подсписков, каждый из которых содержит путь и объект для скачивания.
        """

        for elem in model:
            # print(path)
            if hasattr(elem, 'children'):
                if elem.children:
                    download_array = self.download_urls(elem.children, elem.path)
            else:
                download_array.append([path, elem])

        return download_array

    def download(self,
                 urls: List[List[Union[str, 'YandexInstance']]], #Ожидают return download_urls
                 resp_id: str = 'id1', #id Загрузки все, что полсе /d/ или /i/
                 base_path: str = '../response') -> None:  # base_path - путь, в котором хранятся загрузки
        """
                Загружает файлы, создавая необходимые папки.

                :param urls: Список кортежей, каждый из которых содержит путь к папке и объект для скачивания.
                :param base_path: Базовый путь для сохранения файлов (по умолчанию './response').
                :param resp_id: Идентификатор ответа, добавляемый к пути (по умолчанию '/id1').
                :return: None
        """

        for folder_path, file in urls:

            full_folder_path = os.path.join(base_path + '/' + resp_id + folder_path)
            print(full_folder_path)
            # Создаём все необходимые папки (если они не существуют)
            os.makedirs(full_folder_path,
                        exist_ok=True)  # exist_ok=True предотвращает ошибку, если папка уже существует


            file.download(full_folder_path)

if __name__ == '__main__':
    pk3 = 'https://disk.yandex.ru/i/c_23QH5Z9sv1Cw'
    pk = 'https://disk.yandex.ru/d/huOF6MZIm1oSlg'
    pk2 = 'https://disk.yandex.ru/d/E3z5Ygcd8JkFSw'
    pk4 = 'https://disk.yandex.ru/d/MJ_0Fvouk2ZS0A'

    x = Session(pk4)

    model = x.get_model()

    download_urls = x.download_urls(model)

    x.download(download_urls, 'id4')
