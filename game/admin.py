from django.contrib import admin
from .models import Mission, Question, UserProfile, UserMissionProgress
from django.contrib import messages
from .admin_actions import (
    create_trade_route_questions,
    create_castle_restoration_questions,
    create_grand_tournament_questions
)

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    actions = [
        create_trade_route_questions,
        create_castle_restoration_questions,
        create_grand_tournament_questions
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'story_title', 'description', 'mission_type', 'order', 'is_active')
        }),
        ('Learning Content', {
            'fields': ('key_concepts', 'best_practices', 'npc_dialogue'),
            'description': 'Add the learning content for this mission'
        }),
        ('Rewards', {
            'fields': ('xp_reward',)
        }),
    )
    list_display = ('story_title', 'title', 'mission_type', 'order', 'is_active')
    list_filter = ('mission_type', 'is_active')
    search_fields = ('title', 'story_title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Mission Information', {
            'fields': ('mission', 'scenario_title')
        }),
        ('Question Content', {
            'fields': ('scenario', 'text')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
        }),
        ('Feedback', {
            'fields': ('explanation', 'consequence_a', 'consequence_b', 'consequence_c', 'consequence_d')
        })
    )
    list_display = ('scenario_title', 'mission', 'correct_option')
    list_filter = ('mission', 'correct_option')
    search_fields = ('scenario_title', 'text')
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'total_score', 'xp_points')
    actions = ['reset_progress']

    def reset_progress(self, request, queryset):
        for profile in queryset:
            # Reset profile stats
            profile.total_score = 0
            profile.xp_points = 0
            profile.title = "Apprentice Project Manager"
            profile.save()
            
            # Reset mission progress
            UserMissionProgress.objects.filter(user=profile.user).delete()
            
        messages.success(request, f"Successfully reset progress for {len(queryset)} users.")
    reset_progress.short_description = "Reset selected users' progress"

@admin.register(UserMissionProgress)
class UserMissionProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'mission', 'completed', 'score', 'completed_at')
    list_filter = ('completed', 'mission')
    actions = ['reset_mission_progress']

    def reset_mission_progress(self, request, queryset):
        queryset.delete()
        messages.success(request, "Successfully reset mission progress.")
    reset_mission_progress.short_description = "Reset selected mission progress"