from django.db import models

class PublicKey(models.Model):
    key = models.CharField(max_length=512, help_text="Введите ваш публичный ключ")

    def __str__(self):
        return self.key