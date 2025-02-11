from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('mission/<int:mission_id>/take-quiz/', views.take_quiz, name='take_quiz'),
    path('mission/<int:mission_id>/submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path('mission/<int:mission_id>/results/', views.mission_results, name='mission_results'),
    path('quiz/<int:mission_id>/results/', views.quiz_results, name='quiz_results'),
    path('progress/', views.player_progress, name='player_progress'),
]