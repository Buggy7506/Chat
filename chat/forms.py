from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
      email = forms.EmailField(required=True)
      first_name = forms.CharField(max_length=30, required=True)
      last_name = forms.CharField(max_length=30, required=True)
      profile_picture = forms.ImageField(required=False)
class Meta:
    model = User
    fields = ("username", "email", "first_name", "last_name", "password1", "password2", "profile_picture")      
