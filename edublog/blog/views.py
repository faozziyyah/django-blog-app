from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Comment, Category, Theme
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from itertools import chain
import random
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin


# Create your views here.
def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/index')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')

    else:
        return render(request, 'login.html')

@login_required(login_url='login_user')
def logout(request):
    auth.logout(request)
    return redirect('/')

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('register')
        
    else:
        return render(request, 'register.html')

# profile page
@login_required(login_url='login_user')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

# home page
@login_required(login_url='login_user')
def index(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    categorys = Category.objects.all()
    #posts_lists = Post.objects.all().order_by('-created_at')

    month = month.title()
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    cal = HTMLCalendar().formatmonth(year, month_number)

    # get current year
    now = datetime.now()
    current_year = now.year

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    p = Paginator(Post.objects.all().order_by('-created_at'), 2)
    page = request.GET.get('page')
    posts = p.get_page(page)
    nums = "a" * posts.paginator.num_pages

    if Theme.objects.filter(user=request.user.username).exists():
        color = Theme.objects.get(user=request.user.username).color
        color2 = Theme.objects.get(user=request.user.username).color2
    else:
        color = 'white'
        color2 = 'black'

    return render(request, 'index.html', {'user_profile': user_profile, 'categorys': categorys,  'posts': feed_list, 'posts': posts, 'nums': nums, "current_year": current_year, 'color': color, 'color2': color2, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

# add post page
@login_required(login_url='login_user')
def add_post(request):
    submitted = False
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            #form.save()
            return HttpResponseRedirect('/add_post?submitted=True')
    else:
        form = PostForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'addpost.html', {'form': form, 'submitted': submitted})

# show individual post
@login_required(login_url='login_user')
def show_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    comments = post.comments.all()

    new_comment = None
     # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'postdetails.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})

# delete post
@login_required(login_url='login_user')
def delete_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    post.delete()

    return redirect('index')

# edit post
@login_required(login_url='login_user')
def update_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('index')

    return render(request, 'updatepost.html', {'post': post, 'form': form})

# like post
@login_required(login_url='login_user')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('index')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('index')

# settings
@login_required(login_url='login_user')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('settings')
    return render(request, 'settings.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('index')

# search post
def search_posts(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        posts = Post.objects.filter(title__contains=searched)

        return render(request, 'search.html', {'searched': searched, 'posts': posts})
    else:
        return render(request, 'search.html', {})

# admin approval page
def admin_approval(request):
    post_count = Post.objects.all().count()
    user_count = User.objects.all().count()

    post_list = Post.objects.all().order_by('title')

    p = Paginator(Post.objects.all().order_by('title'), 3)
    page = request.GET.get('page')
    post_list = p.get_page(page)
    nums = "a" * post_list.paginator.num_pages

    if request.user.is_superuser:

        if request.method == 'POST':
            id_list = request.POST.getlist('boxes')

            #uncheck all events
            post_list.update(approved=False)

            for x in id_list:
                Post.objects.filter(pk=int(x)).update(approved=True)

            messages.success(request, ("Post List Approval Has Been Updated!"))
            return redirect('admin-approval')

        else:
            return render(request, 'adminapproval.html', {'post_list': post_list, 'post_list': post_list, 'nums': nums, 'post_count': post_count, 'user_count': user_count})

    else:
        messages.success(request, ("You Aren't Authorized to View This Page!"))
        return redirect('index')

    return render(request, 'adminapproval.html', {'post_list': post_list})

# about page
def about_page(request):
    return render(request, 'about.html', {})

# show category
def show_category(request, category_id):
    #user_profile = Profile.objects.get(user=request.user)
    category = Category.objects.get(pk=category_id)
    category_posts = Post.objects.filter(category__in=[category])

    context = {
        'category_posts': category_posts,
        'category': category,
    }
    return render(request, 'about.html', context)

# reset password
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password-reset.html'
    email_template_name = 'password-reset-email.html'
    subject_template_name = 'password-reset-subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('index')

# theme
def theme(request):
    color = request.GET.get('color')
    color2 = request.GET.get('color2')

    if color == 'dark' or color2 == 'dark':
        if Theme.objects.filter(user=request.user.username).exists():
            user_theme = Theme.objects.get(user=request.user.username)
            user_theme.user = request.user.username
            user_theme.color = 'darkblue'
            user_theme.color2 = 'white'
            user_theme.save()
        else:
            user2 = Theme(user=request.user.username, color='darkblue', color2='white')
            user2.save()

    elif color == 'light' or color2 == 'light':
        if Theme.objects.filter(user=request.user.username).exists():
            user_theme1 = Theme.objects.get(user=request.user.username)
            user_theme1.user = request.user.username
            user_theme1.color = 'white'
            user_theme1.color2 = 'black'
            user_theme1.save()
        else:
            user4 = Theme(user=request.user.username, color='white', color2='black')
            user4.save()

    return redirect('index')