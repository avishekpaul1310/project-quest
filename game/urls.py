from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('mission/<int:mission_id>/quiz/', views.mission_quiz, name='mission_quiz'),
]