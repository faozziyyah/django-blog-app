from django import forms
from django.forms import ModelForm
from .models import Profile, Post, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PostForm(ModelForm):
    class Meta:
        model = Post
        #fields = "__all__"
        fields = ( 'title', 'user', 'content', 'image')
        labels = {
            'title': 'Title',
            'user': 'Username',
            'content': 'Post',
            'image': '',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input ', 'placeholder': 'Title'}),
            'user': forms.TextInput(attrs={'class': 'input ', 'placeholder': 'Username'}),
            'attendees': forms.SelectMultiple(attrs={'class': 'form-select', 'placeholder': 'Attendees'}),
            'content': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Content'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('user', 'body')
        labels = {
            'user': 'user',
            'body': 'body',
        }
        widgets = {
            'user': forms.TextInput(attrs={'class': 'input ', 'placeholder': 'Username'}),
            'body': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Content'}),
        }