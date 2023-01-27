from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date, datetime

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Theme(models.Model):
    color = models.CharField(max_length=1000)
    color2 = models.CharField(max_length=1000, default='')
    user = models.CharField(max_length=1000)

    def __str__(self):
        return self.user

class Category(models.Model):
    user = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images', default='128x128.png')

    def __str__(self):
        return self.user

class Post(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=100)
    user = models.CharField(max_length=100, default=False)
    image = models.ImageField(upload_to='post_images', default='1280x960.png')
    content = models.TextField()
    category = models.ManyToManyField(Category)
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    approved = models.BooleanField('Approved', default=False)

    def __str__(self):
        return self.user

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.CharField(max_length=100)
    body = models.TextField()
    created_on = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.user)

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user