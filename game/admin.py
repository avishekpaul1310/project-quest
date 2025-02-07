from django.contrib import admin
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
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

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('question__mission', 'is_correct')
    search_fields = ('text',)    

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score', 'current_mission')
    list_filter = ('current_mission',)
    search_fields = ('user__username',)
    readonly_fields = ('total_score',)

@admin.register(PlayerAnswer)
class PlayerAnswerAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'selected_choice', 'is_correct')
    list_filter = ('is_correct', 'question__mission')
    search_fields = ('player__user__username',)
    readonly_fields = ('is_correct',)