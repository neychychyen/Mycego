from celery import shared_task
from celery.result import AsyncResult


import parser.main as parser
import parser.database_manipulation as manipulation
import file_parser.file_parser as parser_os

@shared_task(bind=True)
def start(self, pk):
    result = manipulation.start(pk)

    # Очистка (например, удаление результата или завершение задачи)
    if result:
        self.backend.cleanup()  # Очистить результаты задачи, если она завершена
    return result


def isAvailable(pk):
    model = manipulation.databaseInstance(pk)

    result = model.isCreated()
    if result[0]:
        if not model.isReady(result[1][0]):
            return True, (False, 'Элемент скачивается, пожалуйта, подождите')
        else:
            return True, (True, result[1][1])
    else:
        return False


def return_crop_url(pk):
    x = parser.Session(pk)
    return x.get_info()


def return_files(croped):
    path = '../response/'
    identification = croped
    return parser_os.find_files_in_directory(path, identification)