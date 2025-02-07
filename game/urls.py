from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('mission/<int:mission_id>/submit/', views.submit_answer, name='submit_answer'),
]