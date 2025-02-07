from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Existing URLs
    path('', views.dashboard, name='dashboard'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
    
    # New Quiz URLs
    path('mission/<int:mission_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('mission/<int:mission_id>/results/', views.mission_results, name='mission_results'),
]