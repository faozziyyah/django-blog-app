from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount, Comment, Category, Theme

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(LikePost)
admin.site.register(Comment)
admin.site.register(FollowersCount)
admin.site.register(Theme)