from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "pub_date", "category", "location", "image"]

        widgets = {
            "pub_date": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",  # Формат для HTML5 виджета
                attrs={"type": "datetime-local"},
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
