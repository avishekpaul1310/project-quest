from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('mission/<int:mission_id>/submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path('mission/<int:mission_id>/results/', views.quiz_results, name='quiz_results'),
]