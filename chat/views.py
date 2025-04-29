from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import Profile
from .models import Message
from django.db.models import Q, Count

from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def home(request):
    if request.user.is_authenticated:
        users = User.objects.exclude(username=request.user.username)
        return render(request, 'chat/home.html', {'users': users})
    else:
        return redirect('login')
for u in users:    

        unread = Message.objects.filter(sender=u, receiver=request.user, seen=False).count()
        user_data.append({'user': u, 'unread': unread})

def signup_view(request):
    if request.method == 'POST':
      if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
           user = form.save(commit=False)
           user.email = form.cleaned_data['email']
           user.first_name = form.cleaned_data['first_name']
           user.last_name = form.cleaned_data['last_name']
           user.save()
           return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'chat/signup.html', {'form':form})   
    messages.error(request, "Invalid credentials")
    return render(request, 'chat/login.html' )
    user = User.objects.create_user(username=username, password=password)
    login(request, user)
    return redirect('home')
    return render(request, 'chat/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials" )
    return render(request, 'chat/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def chat_view(request, username):
    friend = User.objects.get(username=username)
    messages = Message.objects.filter(
        sender__in=[request.user, friend],
        receiver__in=[request.user, friend]
    ).order_by('timestamp')
    return render(request, 'chat/chat.html', {
        'friend_username': username,
        'messages': messages
    })



@login_required
def profile_view(request):
    if request.method == 'POST':
        pic = request.FILES['profile_pic']
        profile = request.user.profile
        profile.image = pic
        profile.save()
        return redirect('home')
    return render(request, 'chat/profile.html')
