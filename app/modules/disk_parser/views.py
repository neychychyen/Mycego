# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import PublicKeyForm

def submit_public_key(request):
    if request.method == 'POST':
        form = PublicKeyForm(request.POST)
        if form.is_valid():
            # Получаем объект ключа
            public_key = form.save()

            # Перенаправляем на success с переданным ключом
            return redirect(f'/success/?path={public_key.key}')
    else:
        form = PublicKeyForm()

    return render(request, 'disk_parser/submit_key.html', {'form': form})

def success(request):
    # Извлекаем параметр 'path' из строки запроса
    public_key = request.GET.get('path', 'Ключ не передан')

    return HttpResponse(f"Публичный ключ: {public_key} в обработке!")
