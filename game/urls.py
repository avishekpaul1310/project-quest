from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mission/<int:mission_id>/', views.mission_learning, name='mission_learning'),
    path('mission/<int:mission_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('mission/<int:mission_id>/results/', views.mission_results, name='mission_results'),
]