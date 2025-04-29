from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import Profile, Message
from django.db.models import Q


def home(request):
    if request.user.is_authenticated:
        users = User.objects.exclude(username=request.user.username)
        user_data = []
        for u in users:
            unread = Message.objects.filter(sender=u, receiver=request.user, seen=False).count()
            user_data.append({'user': u, 'unread': unread})
        return render(request, 'chat/home.html', {'users': user_data})
    else:
        return redirect('login')


def signup_view(request):
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
    return render(request, 'chat/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'chat/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def chat_view(request, username):
    friend = User.objects.get(username=username)

    # Mark messages from friend as seen
    Message.objects.filter(sender=friend, receiver=request.user, seen=False).update(seen=True)

    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=friend) | Q(sender=friend, receiver=request.user)
    ).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'friend_username': username,
        'messages': messages_qs
    })


@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'profile_pic' in request.FILES:
            profile = request.user.profile
            profile.image = request.FILES['profile_pic']
            profile.save()
        return redirect('home')
    return render(request, 'chat/profile.html')
