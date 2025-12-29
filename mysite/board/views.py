from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from .models import Message
import logging

 # Problem A09, logger is not used
logger = logging.getLogger(__name__)


def index(request):
    # Problem A05, raw SQL is used without parameters
    search_query = request.GET.get('search', '')
    
    if search_query:
        query = f"SELECT * FROM board_message WHERE content LIKE '%{search_query}%' ORDER BY created_at DESC"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            messages = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        messages = Message.objects.all()
    
    # FIX, use parameterized queries in odrer to prevent SQL injection
    # if search_query:
    #     query = "SELECT * FROM board_message WHERE content LIKE %s ORDER BY created_at DESC"
    #     with connection.cursor() as cursor:
    #         cursor.execute(query, [f'%{search_query}%'])
    #         columns = [col[0] for col in cursor.description]
    #         messages = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # else:
    #     messages = Message.objects.all()
    
    return render(request, 'board/index.html', {'messages': messages})

def login_view(request):
    # Problem A07, login attempts dont have rate limiting or logging
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    
        # FIX, log failed login attempts
        # logger.warning(f'Failed login attempt for user: {username} from IP: {request.META.get("REMOTE_ADDR")}')
    
    # FIX, add rate limiting to login attempts
    # from django.core.cache import cache
    # from django.http import HttpResponse
    # 
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     ip = request.META.get('REMOTE_ADDR')
    #     cache_key = f'login_attempts_{ip}'
    #     attempts = cache.get(cache_key, 0)
    #     
    #     if attempts >= 5:
    #         logger.warning(f'Rate limit exceeded for IP: {ip}')
    #         return HttpResponse('Too many login attempts. Try again later.', status=429)
    #     
    #     user = authenticate(request, username=username, password=password)
    #     if user is not None:
    #         login(request, user)
    #         logger.info(f'Successful login for user: {username} from IP: {ip}')
    #         cache.delete(cache_key)
    #         return redirect('index')
    #     else:
    #         logger.warning(f'Failed login attempt for user: {username} from IP: {ip}')
    #         cache.set(cache_key, attempts + 1, 300)  # 5 minute timeout
    
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

def delete_message(request, message_id):
    message = Message.objects.get(id=message_id)
    # Problem A09, message deletions are not logged
    message.delete()
    return redirect('index')
    
    # FIX, check if the user is the owner before deleting
    # FIX, add logging for deletions
    # if message.author == request.user:
    #     logger.warning(f'User {request.user.username} deleted message(s) {message_id}')
    #     message.delete()
    #     return redirect('index')
    # else:
    #     logger.warning(f'Unauthorized deletion attempt by {request.user.username} on message(s) {message_id}')
    #     return redirect('index')
