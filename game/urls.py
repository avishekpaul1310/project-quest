from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('missions/', views.available_missions, name='available_missions'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('progress/', views.player_progress, name='progress'),
    path('stats/', views.user_stats, name='user_stats'),
]