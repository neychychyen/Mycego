from __future__ import absolute_import, unicode_literals

# Эта строка необходима для того, чтобы Celery инициализировался при старте Django
from .celery import app as celery_app

__all__ = ('celery_app',)