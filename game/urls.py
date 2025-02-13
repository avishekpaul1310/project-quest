from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('mission/<int:mission_id>/results/', views.quiz_results, name='quiz_results'),
]