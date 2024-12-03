import requests
import os
from typing import List, Dict, Union, Any, Optional, Callable, Tuple


class Session:
    public_url = 'https://cloud-api.yandex.net/v1/disk/public/resources'

    def __init__(self, public_key: str) -> None:
        self.public_key: str = public_key
        # print(f'Инициализирован Session c {self.public_key}')

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
    def __make_yandex_instance_in_dict(json: Dict[str, str]) -> dict[str, Any]:

        dictionary = {
            'name': json['name'],
            'file': json['file'],
            'mime_type': json['mime_type'],
            'md5': json['md5']
        }

        return dictionary

    @staticmethod
    def __make_folder_in_dict(json: Dict[str, str]) -> dict[str, Any]:
        dictionary = {
            'path': json['path'],
            'type': json['type'],
            'children': []
        }

        return dictionary

    def __get_tree(self, path: str) -> List[Dict[str, Any]]:
        """
                Метод для получения данных о дереве элементов по заданному пути.
                :param path: Путь для получения данных.
        """
        result = self.__get_json(self.public_url, public_key=self.public_key, path=path)
        return self.__parse_data(result)

    def __parse_elem(self, json_elem: Dict[str, Any]) -> Dict[str, Any]:
        """
                Метод для парсинга элемента JSON и создания соответствующего объекта.

                :param json_elem: Элемент JSON, содержащий информацию о папке или файле.
                :return: Словарь с элемментами
        """

        if json_elem['type'] == 'dir':
            folder = self.__make_folder_in_dict(json_elem)
            result = self.__get_tree(folder['path'])
            folder['children'] = result
            return folder  # Вызываем соответствующую функцию
        else:
            return self.__make_yandex_instance_in_dict(json_elem)

    def __parse_data(self, json_response: Dict[str, Any]) -> List[Dict[str, Any]]:

        """
                Метод для парсинга данных из JSON-ответа, если это папка, обработки каждого элемента и возврата списка объектов.

                :param json_response: Ответ в формате JSON, содержащий ключ '_embedded' с элементами.
                :return: Список объектов-Словарей
        """

        result = json_response['_embedded']['items']
        result = [self.__parse_elem(item) for item in result]

        return result

    def get_info(self) -> Tuple[str, str, str, str]:
        """
                Получает информацию о публичном ключе и публичном URL.

                :return: id пути, public_url, public_key, тип ссылки (файл или папка)
        """

        def crop_url(url: str) -> Tuple[str, str]:
            """
                # Разделяем url по символу "/"
            :param url: str
            :return: возвращает id пути, тип ссылки (i - один файл, d - директория
            """

            parts = url.split('/')  # Разделяем строку по символу "/"
            return parts[-1], parts[-2]

        info = self.__get_json(self.public_url, public_key=self.public_key)
        cropped = crop_url(info['public_url'])

        return cropped[0], info['public_url'], info['public_key'], cropped[1]

    def get_model(self) -> Optional[List[Dict[str, Any]]]:

        """
                Возвращает массив из элементов или ничего, если Неправильно

        """
        info = self.get_info()

        result = self.__get_json(self.public_url, public_key=self.public_key)

        # Если директория
        if info[-1] == 'd':
            return self.__parse_data(result)

        # Если файл
        elif info[-1] == 'i':
            return [self.__parse_elem(result)]

        else:
            return None

    def download(self) -> bool:
        try:
            model = self.get_model()
            info = self.get_info()

            download_dir = '../response'

            id = info[0]

            def get_all_paths(data: Dict[str, Any], parent_path: str = '') -> List[str]:
                paths = []
                for item in data:
                    if 'path' in item:
                        full_path = item['path']
                        paths.append(full_path)

                    # If the item has 'children', recursively process them
                    if 'children' in item:
                        paths.extend(get_all_paths(item['children'], parent_path=full_path))

                return paths

            def get_file_paths_and_info(data: Dict[str, Any], parent_path: str = '', files_info: List[Any] = []) -> \
            List[Any]:
                """Возвращает пути файлов и информацию о них"""

                for item in data:
                    # Safely access the 'path' key using .get()
                    # print(item)
                    if item.get('path'):
                        get_file_paths_and_info(item['children'], item['path'], files_info)
                    else:
                        files_info.append([parent_path, item])

                return files_info

            def mkdirs(dirs: List, id: str, before: str = download_dir) -> None:
                if dirs:
                    for elem in dirs:

                        os.makedirs(before + '/' + id + elem, exist_ok=True)
                else:
                    os.makedirs(before + '/' + id, exist_ok=True)

            def download_from_path_and_info(data: List[Any], id: str, before: str = download_dir) -> None:
                for elem in data:
                    url = elem[1]['file']
                    name = elem[1]['name']
                    path = before + '/' + id

                    response = requests.get(url, stream=True)

                    # Проверка успешности запроса
                    if response.status_code == 200:
                        with open(path + elem[0] + '/' + name, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        # print(f"Файл {self.name} успешно скачан!")
                    else:
                        pass

            all_paths = get_all_paths(model)

            mkdirs(all_paths, id)

            paths_and_info = get_file_paths_and_info(model)

            download_from_path_and_info(paths_and_info, id)

            return True
        except Exception as e:
            #print(e)
            return False


if __name__ == '__main__':
    pk3 = 'https://disk.yandex.ru/i/c_23QH5Z9sv1Cw'
    pk = 'https://disk.yandex.ru/d/huOF6MZIm1oSlg'
    pk2 = 'https://disk.yandex.ru/d/E3z5Ygcd8JkFSw'
    pk4 = 'https://disk.yandex.ru/d/MJ_0Fvouk2ZS0A'

    x = Session(pk2)
    print(x.download())
