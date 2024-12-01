from typing import List, Tuple, Optional

from main import *

import os

import psycopg2
from psycopg2 import sql

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
DATABASE_URL = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"


class ParserInstance:
    def __init__(self, public_key: str) -> None:
        self.instance = YandexDisk(public_key)

    def get_info_from_model(self) -> Tuple[str]:
        """
            Возвращает публичный ключ, ссылку, и id ссылки из модели (не из бд)
            :return: (self.__crop_url(info['public_url']), info['public_url'], info['public_key'])
        """
        return self.instance.get_info()
    def isExist(self) -> bool:
        """
            Подключается к бд download и проверяет, существует ли name
            :return: bool
        """

        name = self.get_info_from_model()[0]

        try:
            # Подключаемся к базе данных
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            # Пишем SQL-запрос для поиска записи с данным name
            query = sql.SQL("SELECT EXISTS (SELECT 1 FROM download WHERE name = %s);")
            cursor.execute(query, (name,))

            # Получаем результат
            exists = cursor.fetchone()[0]

            # Закрываем курсор и соединение
            cursor.close()
            connection.close()

            return exists
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            return False

    def create_entry(self) -> None:
        """
            Создает первичную запись в таблице download и затем в таблице response.
            Если возникает ошибка, откатывает транзакцию.
        """

        def create_download(name: str, url: str, public_key: str, connection, cursor) -> bool:
            """
                Подключается к бд download и добавляет name: str, url: str, public_key: str запись
                :return: True - успешно, False - с ошибкой
            """
            try:
                # Пишем SQL-запрос для вставки записи
                query = sql.SQL("""
                    INSERT INTO download (name, url, public_key)
                    VALUES (%s, %s, %s);
                """)

                # Выполняем запрос с переданными параметрами
                cursor.execute(query, (name, url, public_key))
                return True
            except Exception as e:
                print(f"Ошибка при добавлении записи в таблицу download: {e}")
                return False

        def create_response(download_name: str, connection, cursor) -> bool:
            """
                Создает запись в таблице response, используя имя из таблицы download
                :param download_name: имя записи из таблицы download
                :return: True - если запись успешно создана, False - если произошла ошибка
            """

            def get_download_id_by_name(name: str, cursor) -> Optional[int]:
                """
                    Получает id из таблицы download по имени
                    :param name: имя записи в таблице download
                    :return: id записи
                """
                try:
                    # Пишем SQL-запрос для получения id по имени
                    query = sql.SQL("SELECT id FROM download WHERE name = %s;")
                    cursor.execute(query, (name,))

                    # Получаем результат
                    result = cursor.fetchone()

                    if result:
                        return result[0]  # Возвращаем id
                    else:
                        return None  # Если запись не найдена
                except Exception as e:
                    print(f"Ошибка при получении id записи: {e}")
                    return None

            # Получаем id из таблицы download по имени
            download_id = get_download_id_by_name(download_name, cursor)

            if download_id is None:
                return False  # Если не нашли id, то ошибка

            try:
                # Пишем SQL-запрос для вставки записи в таблицу response
                query = sql.SQL("""
                    INSERT INTO response (download_id, ready_to_use)
                    VALUES (%s, %s);
                """)

                # Выполняем запрос с параметрами (download_id, ready_to_use=False)
                cursor.execute(query, (download_id, False))
                return True
            except Exception as e:
                print(f"Ошибка при добавлении записи в таблицу response: {e}")
                return False

        # Получаем информацию из модели
        entry_instance = self.get_info_from_model()

        #Производим запись
        try:
            # Подключаемся к базе данных
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            # Начинаем транзакцию
            connection.autocommit = False

            # Создаем запись в таблице download
            if not create_download(*entry_instance, connection, cursor):
                connection.rollback()  # Откатываем транзакцию при ошибке
                print("Ошибка при добавлении записи в таблицу download.")
                return

            # Создаем запись в таблице response
            if not create_response(entry_instance[0], connection, cursor):
                connection.rollback()  # Откатываем транзакцию при ошибке
                print("Ошибка при добавлении записи в таблицу response.")
                return

            # Если все прошло успешно, подтверждаем транзакцию
            connection.commit()

            print("Записи успешно добавлены в download и response.")
        except Exception as e:
            print(f"Ошибка при выполнении транзакции: {e}")
            if connection:
                connection.rollback()  # Откатываем транзакцию в случае ошибки
        finally:
            if connection:
                cursor.close()
                connection.close()

    def check_status(self) -> bool:
        """
            Проверяет ready_to_use из response
            :return: bool - возвращает True, если ready_to_use == True, иначе False
        """
        name = self.get_info_from_model()[0]  # Получаем имя из модели

        try:
            # Подключаемся к базе данных
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            # Пишем SQL-запрос для получения значения ready_to_use по имени
            query = sql.SQL("""
                SELECT ready_to_use
                FROM response
                JOIN download ON response.download_id = download.id
                WHERE download.name = %s;
            """)
            cursor.execute(query, (name,))

            # Получаем результат
            result = cursor.fetchone()

            # Закрываем курсор и соединение
            cursor.close()
            connection.close()

            # Если результат найден, возвращаем состояние ready_to_use
            if result is not None:
                return result[0]  # True или False
            else:
                return False  # Если запись не найдена, возвращаем False
        except Exception as e:
            print(f"Ошибка при проверке состояния в базе данных: {e}")
            return False

    def change_status(self, ready_to_use: bool) -> bool:
        """
            Меняет ready_to_use из response на {ready_to_use}
            :return: Возвращает True, если успешно, иначе False
        """
        name = self.get_info_from_model()[0]  # Получаем имя из модели

        try:
            # Подключаемся к базе данных
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            # Пишем SQL-запрос для обновления значения ready_to_use
            query = sql.SQL("""
                UPDATE response
                SET ready_to_use = %s
                FROM download
                WHERE response.download_id = download.id
                AND download.name = %s;
            """)

            # Выполняем запрос с переданными параметрами
            cursor.execute(query, (ready_to_use, name))

            # Проверяем, были ли обновлены записи
            if cursor.rowcount > 0:
                connection.commit()  # Подтверждаем транзакцию
                print("Статус успешно обновлён.")
                cursor.close()
                connection.close()
                return True
            else:
                # Если не было затронуто ни одной строки, значит, записи не существует
                print("Запись не найдена или ошибка обновления.")
                cursor.close()
                connection.close()
                return False
        except Exception as e:
            print(f"Ошибка при изменении статуса в базе данных: {e}")
            if connection:
                connection.rollback()  # Откатываем транзакцию в случае ошибки
            return False

    def download_files_from_model(self) -> None:
        """
            Скачивает файлы с модели
            :return: None
        """
        info = self.get_info_from_model()
        model = self.instance.get_model()
        download_urls = self.instance.download_url(model)

        self.instance.download(download_urls, info[0], '../response/')


def start(public_key):
    x = ParserInstance(public_key)
    if not x.isExist():
        x.create_entry()
        model = x.instance.get_model()

    if not x.check_status():
        x.download_files_from_model()
        x.change_status(True)

if __name__ == "__main__":
    public_key = 'https://disk.yandex.ru/d/huOF6MZIm1oSlg'

    start(public_key)







