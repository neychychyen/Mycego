# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import PublicKeyForm
from .tasks import start, return_crop_url, return_files


def submit_public_key(request):
    def crop_url(url):
        parts = url.split('/')  # Разделяем строку по символу "/"
        return parts[-1]


    if request.method == 'POST':
        form = PublicKeyForm(request.POST)
        if form.is_valid():
            # Получаем объект ключа
            public_key = form.save()


            start.delay(public_key.key) #Сюда Celery

            form = PublicKeyForm()
            # Перенаправляем на success с переданным ключом
            return redirect(f'/success/?public_url={return_crop_url(public_key.key)[0]}&public_key={return_crop_url(public_key.key)[2]}')
    else:
        form = PublicKeyForm()

    response = render(request, 'disk_parser/submit_key.html', {'form': form})
    return response

def success(request):
    # Извлекаем параметр 'path' из строки запроса
    public_url = request.GET.get('public_url', None)
    public_key = request.GET.get('public_key', None)

    response = render(request, 'disk_parser/success.html', {'public_url': public_url, 'public_key': public_key})
    return response


from django.http import JsonResponse
from .tasks import isAvailable
def ajax_isAvailable(request):

    status = None
    Warnings = None

    if request.method == 'GET':


        public_key = request.GET.get('public_url', None)


        if public_key:
            result = isAvailable(public_key)

            if not result[0]:
                status = False
                Warnings = 'Элемента не существует, отправтесь на главную страницу и создайте его'

            else:
                if not result[1][0]:
                    status = False
                    Warnings = result[1][1]
                else:
                    status = True
                    Warnings = 'Элемент готов к использованию'
    return JsonResponse({'status': status, 'Warnings': Warnings})



def ajax_get_elements(request):

    elements = []

    if request.method == 'GET':
        public_key = request.GET.get('public_url', None)
        if public_key:
            elements = return_files(public_key)

    return JsonResponse({'elements': elements})


from django.http import FileResponse, Http404
import os
from django.conf import settings
from io import BytesIO
import zipfile



def download_file(request):
    paths = request.GET.getlist('paths')  # Получаем массив путей из параметров
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for path in paths:
            pre_path = '../response/'
            file_path = os.path.join(pre_path, path)
            print(file_path)
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=os.path.basename(file_path))

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=files.zip'
    return response

# def download_file(request):
#     # Путь к файлу на сервере
#     if request.method == 'GET':
#         zip_buffer = BytesIO()
#
#         path = request.GET.get('path', None)
#
#         file_path = '../response/' + path
#
#
#     # Проверяем, существует ли файл
#         if not os.path.exists(file_path):
#             raise Http404("Файл не найден")
#
#     # Возвращаем файл для скачивания
#         return FileResponse(open(file_path, 'rb'), as_attachment=True)