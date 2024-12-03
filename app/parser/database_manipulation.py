import os

import psycopg2
from psycopg2 import sql

from parser.parser_instance import *

from typing import List, Tuple, Optional, Any

# Загрузка переменных окружения
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
DATABASE_URL = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"

class databaseInstance:
    def __init__(self, public_key: str) -> None:
        self.public_key = public_key

    def __connect(self):
        """
        Устанавливает соединение с базой данных через DATABASE_URL.
        :return: Соединение и курсор для работы с базой.
        """
        conn = psycopg2.connect(DATABASE_URL)
        return conn, conn.cursor()

    def isCreated(self) -> list[bool, Optional[Tuple[int, str]]]:
        """
        Проверить, создан ли экземпляр с данным public_key в таблице download.
        :return: True/False
        """
        conn, cursor = self.__connect()
        try:

            def crop_url(url: str) -> str:
                parts = url.split('/')  # Разделяем строку по символу "/"
                return parts[-1]

            name = crop_url(self.public_key)

            query = "SELECT EXISTS(SELECT 1 FROM download WHERE public_key = %s or name = %s);"
            cursor.execute(query, (self.public_key, name))
            boolean = cursor.fetchone()



            query = "SELECT id, name FROM download WHERE public_key = %s or name = %s;" #SELECT name FROM download WHERE public_key = 'https://disk.yandex.ru/d/huOF6MZIm1oSlg' or url = 'https://disk.yandex.ru/d/huOF6MZIm1oSlg';
            cursor.execute(query, (self.public_key, name))
            result = cursor.fetchone()
            return boolean[0], [result[0], name]

        except:
            return False,

        finally:
            cursor.close()
            conn.close()

    def isReady(self, id: int) -> bool:
        """
        Проверить готовность записи с заданным id в таблице response.
        :return: True/False
        """
        conn, cursor = self.__connect()
        try:
            query = "SELECT ready_to_use FROM response WHERE download_id = %s;"
            cursor.execute(query, (id,))
            result = cursor.fetchone()
            return result[0] if result else False
        finally:
            cursor.close()
            conn.close()

    def create(self) -> None:
        """
        Создает новый экземпляр записи в таблице download с данным public_key.
        :return: None
        """
        first_init(self.public_key)

def start(public_key:str) -> Tuple[bool, Optional[Tuple[bool, str]]]:
    x = databaseInstance(public_key)
    try:
        result = x.isCreated()
        if result[0]:
            if not x.isReady(result[1][0]):
                return True, (False, 'Элемент скачивается, пожалуйта, подождите')
            else:
                return True, (True, result[1][1])
        else:
            x.create()
            return start(public_key)
    except:
        return False


if __name__ == '__main__':
    pk3 = 'https://disk.yandex.ru/i/c_23QH5Z9sv1Cw'
    pk = 'https://disk.yandex.ru/d/huOF6MZIm1oSlg'
    pk2 = 'https://disk.yandex.ru/d/E3z5Ygcd8JkFSw'
    public_key = 'https://disk.yandex.ru/d/huOF6MZIm1oSlg'
    print(start(pk))
