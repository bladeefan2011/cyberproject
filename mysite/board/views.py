from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message

# Create your views here.

def index(request):
    messages = Message.objects.all()
    return render(request, 'board/index.html', {'messages': messages})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    return render(request, 'board/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('index')
    return render(request, 'board/register.html')

@login_required
def post_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(author=request.user, content=content)
        return redirect('index')
    return redirect('index')
