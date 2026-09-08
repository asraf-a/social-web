from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


class CustomLogoutView(auth_views.LogoutView):
    """
    Modern Django 5+ LogoutView defaults to requiring POST.
    Subclassing allows both POST (recommended modern security standard)
    and GET (for seamless navigation links and educational testing).
    """
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Educational manual login view from Chapter 4
    path('login-manual/', views.user_login, name='login_manual'),

    # Built-in Authentication Views
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Password Change URLs
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(),
        name='password_change_done'
    ),

    # Password Reset URLs
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),

    # User Registration & Profile Editing
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),

    # People directory & follow system
    path('users/', views.user_list, name='user_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('users/<username>/', views.user_detail, name='user_detail'),
]
