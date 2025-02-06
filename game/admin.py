from django.contrib import admin
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'is_active')
    list_filter = ('is_active',)
    ordering = ('order',)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('mission', 'order', 'text')
    list_filter = ('mission',)
    inlines = [ChoiceInline]
    ordering = ('mission', 'order')

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score', 'current_mission', 'missions_completed')
    filter_horizontal = ('completed_missions',)
    
    def missions_completed(self, obj):
        return obj.completed_missions.count()

@admin.register(PlayerAnswer)
class PlayerAnswerAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__mission')