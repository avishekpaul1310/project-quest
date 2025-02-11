from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('available-missions/', views.available_missions, name='available_missions'),
    path('mission/<int:mission_id>/', views.mission_detail, name='mission_detail'),
]