from django.contrib import admin
from .models import Mission, Question, UserProfile, UserMissionProgress

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'mission_type', 'pmbok_chapter', 'order', 'is_active')
    list_filter = ('mission_type', 'is_active')
    search_fields = ('title', 'description', 'pm_concepts', 'key_concepts')
    
    fieldsets = (
        ('Mission Basics', {
            'fields': ('title', 'mission_type', 'story_title', 'order', 'is_active')
        }),
        ('PMBOK Learning Content', {
            'fields': ('pmbok_chapter', 'key_concepts', 'best_practices'),
            'classes': ('wide',)
        }),
        ('Mission Details', {
            'fields': ('objective', 'pm_concepts', 'description', 'npc_dialogue')
        }),
        ('Rewards', {
            'fields': ('xp_reward',)
        })
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('scenario_title', 'mission', 'correct_option')
    list_filter = ('mission__mission_type', 'mission')
    search_fields = ('scenario_title', 'scenario', 'text')
    
    fieldsets = (
        ('Question Basics', {
            'fields': ('mission', 'scenario_title')
        }),
        ('Scenario', {
            'fields': ('scenario', 'text'),
            'classes': ('wide',)
        }),
        ('Options', {
            'fields': (
                'option_a', 'option_b', 'option_c', 'option_d',
                'correct_option', 'explanation'
            )
        }),
        ('Consequences', {
            'fields': (
                'consequence_a', 'consequence_b',
                'consequence_c', 'consequence_d'
            )
        })
    )

admin.site.register(UserProfile)
admin.site.register(UserMissionProgress)