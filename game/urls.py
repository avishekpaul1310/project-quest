from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('progress/', views.player_progress, name='player_progress'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('mission/<int:mission_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('mission/<int:mission_id>/results/', views.mission_results, name='mission_results'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('stats/', views.user_stats, name='user_stats'),
]