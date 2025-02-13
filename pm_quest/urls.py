from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('game.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='game/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Add a root URL redirect
    path('', lambda request: redirect(reverse_lazy('game:dashboard')), name='root'),
]