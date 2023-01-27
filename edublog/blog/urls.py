from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import ResetPasswordView


urlpatterns = [
    path('', views.signin, name='login'),
    path('index', views.index, name='index'),
    path('theme', views.theme, name='theme'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('settings', views.settings, name='settings'),
    path('signup', views.signup, name='register'),
    path('logout', views.logout, name='logout'),
    path('follow', views.follow, name='follow'),
    path('add_post', views.add_post, name='add-post'),
    path('show_post/<post_id>', views.show_post, name='show-post'),
    path('delete_post/<post_id>', views.delete_post, name='delete-post'),
    path('like-post', views.like_post, name='like-post'),
    path('update_post/<post_id>', views.update_post, name='update-post'),
    path('search_posts', views.search_posts, name='search-posts'),
    path('admin_approval', views.admin_approval, name='admin-approval'),
    path('about_page', views.about_page, name='about'),
    path('show_category/<category_id>', views.show_category, name='show-category'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='password-reset-confirm.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password-reset-confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password-reset-complete.html'),
         name='password_reset_complete'),
]