from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем стандартную настройку Django для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Создаем экземпляр Celery
app = Celery('app')

# Используем настройки из Django (параметры, связанные с Celery)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находит задачи в каждом из приложений Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))