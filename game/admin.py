from django.contrib import admin
from .models import UserProfile, Mission, Question, UserMissionProgress

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_score', 'total_xp', 'title']
    search_fields = ['user__username', 'title']

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'order', 'is_active')
        }),
        ('Mission Details', {
            'fields': ('objective', 'key_concepts', 'best_practices')
        }),
        ('NPC Information', {
            'fields': ('npc_name', 'npc_dialogue')
        }),
        ('Rewards', {
            'fields': ('xp_reward',)
        }),
    )
    list_display = ['title', 'order', 'is_active', 'xp_reward']
    list_editable = ['order', 'is_active', 'xp_reward']
    search_fields = ['title', 'description', 'objective']
    list_filter = ['is_active']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['mission', 'scenario', 'correct_option']
    list_filter = ['mission']
    search_fields = ['scenario', 'explanation']
    fieldsets = (
        (None, {
            'fields': ('mission', 'scenario')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
        }),
        ('Additional Information', {
            'fields': ('explanation',)
        }),
    )

@admin.register(UserMissionProgress)
class UserMissionProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'mission', 'completed', 'score', 'completed_at']
    list_filter = ['completed', 'mission']
    search_fields = ['user__username', 'mission__title']
    readonly_fields = ['completed_at']