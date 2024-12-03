from celery import shared_task
from celery.result import AsyncResult
import logic.download_by_key as logic
import time

# @shared_task
# def my_task():
#     time.sleep(10)  # Имитация долгой работы
#     return 'Task completed'


@shared_task(bind=True)
def start(self, pk):
    result = logic.download_and_process_key(pk)

    # Очистка (например, удаление результата или завершение задачи)
    if result:
        self.backend.cleanup()  # Очистить результаты задачи, если она завершена
    return result