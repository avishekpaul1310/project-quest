from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # These are placeholder URL patterns - we'll implement the views later
    path('', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('mission/<int:mission_id>/submit/', views.submit_answer, name='submit_answer'),
]