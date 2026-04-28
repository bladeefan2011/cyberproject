from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from .models import Message
import logging
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


 # Problem A09, logger is not used
logger = logging.getLogger(__name__)


def index(request):
    # logger.info(f'User {request.user.username if request.user.is_authenticated else "Anonymous"} visited the index page.')
    # Problem A05, raw SQL is used without parameters
    search_query = request.GET.get('search', '')
    
    if search_query:
        query = f"SELECT board_message.id, board_message.content, board_message.created_at, board_message.author_id, auth_user.username as author__username FROM board_message JOIN auth_user ON board_message.author_id = auth_user.id WHERE content LIKE '%{search_query}%' ORDER BY created_at DESC"
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            messages = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        messages = Message.objects.all()
    
    # FIX, use parameterized queries in odrer to prevent SQL injection
    # if search_query:
    #     query = "SELECT board_message.id, board_message.content, board_message.created_at, board_message.author_id, auth_user.username as author__username FROM board_message JOIN auth_user ON board_message.author_id = auth_user.id WHERE content LIKE %s ORDER BY created_at DESC"
    #     with connection.cursor() as cursor:
    #         cursor.execute(query, [f'%{search_query}%'])
    #         columns = [col[0] for col in cursor.description]
    #         messages = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # else:
    #     messages = Message.objects.all()
    
    return render(request, 'board/index.html', {'messages': messages})

def login_view(request):
    # Fixed A07: Added rate limiting and logging
    
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     ip = request.META.get('REMOTE_ADDR')
    #     cache_key = f'login_attempts_{ip}'
    #     attempts = cache.get(cache_key, 0)
        
    #     if attempts >= 5:
    #         logger.warning(f'Rate limit exceeded for IP: {ip}')
    #         return HttpResponse('Too many login attempts.', status=429)
        
    #     user = authenticate(request, username=username, password=password)
    #     if user is not None:
    #         login(request, user)
    #         logger.info(f'Successful login for user: {username} from IP: {ip}')
    #         cache.delete(cache_key)
    #         return redirect('index')
    #     else:
    #         logger.warning(f'Failed login attempt for user: {username} from: {ip}')
    #         cache.set(cache_key, attempts + 1, 300)  # 5 minute timeout
    
    return render(request, 'board/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        # logger.info(f'User logged out: {request.user.username}')
        pass
    logout(request)
    return redirect('index')


#Problem A07: No password validation
# FIX: Now the validation is actually done when we're registering.
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                validate_password(password)
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                # logger.info(f'New user registered and logged in: {username}')
                return redirect('index')
            except ValidationError as e:
                # logger.warning(f'User failed registration due to weak password: {username}')
                return render(request, 'board/register.html', {'error': 'Password too weak.'})
    return render(request, 'board/register.html')

@login_required
def post_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(author=request.user, content=content)
            # logger.info(f'User {request.user.username} posted a message.')
        return redirect('index')
    return redirect('index')

def delete_message(request, message_id):
    message = Message.objects.get(id=message_id)
    
    if message.author == request.user:
        # logger.info(f'User {request.user.username} deleted message {message_id}')
        message.delete()
        return redirect('index')
    else:
        # logger.warning(f'Unauthorized deletion attempt by {request.user.username} on message {message_id}')
        return redirect('index')
