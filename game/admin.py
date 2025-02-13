from django.contrib import admin
from .models import UserProfile, Mission, Question, UserMissionProgress

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('order',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('mission', 'text', 'correct_option')
    list_filter = ('mission',)

@admin.register(UserMissionProgress)
class UserMissionProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'mission', 'completed', 'score')
    list_filter = ('completed', 'mission')

admin.site.register(UserProfile)