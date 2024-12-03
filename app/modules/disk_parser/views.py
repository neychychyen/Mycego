# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import PublicKeyForm
from .tasks import start


def submit_public_key(request):
    if request.method == 'POST':
        form = PublicKeyForm(request.POST)
        if form.is_valid():
            # Получаем объект ключа
            public_key = form.save()

            start.delay(public_key.key) #Сюда Celery

            form = PublicKeyForm()
            # Перенаправляем на success с переданным ключом
            return redirect(f'/success/?path={public_key.key}')
    else:
        form = PublicKeyForm()

    response = render(request, 'disk_parser/submit_key.html', {'form': form})

    # # Отключаем кэширование, добавляем заголовки
    # response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    # response['Pragma'] = 'no-cache'
    # response['Expires'] = '0'

    return response

def success(request):
    # Извлекаем параметр 'path' из строки запроса
    public_key = request.GET.get('path', 'Ключ не передан')

    return HttpResponse(f"Публичный ключ: {public_key} в обработке!")
