from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

# Главная страница для авторизованных пользователей
@login_required
def home(request):
    return render(request, 'auth/home.html')

# Логин
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'auth/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'auth/login.html')

# Регистрация
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {'error': 'Пользователь уже существует'})
        User.objects.create_user(username=username, password=password)
        return redirect('login')
    return render(request, 'auth/register.html')

# Выход
def user_logout(request):
    logout(request)
    return redirect('login')