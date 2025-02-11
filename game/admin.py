from django.contrib import admin
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('mission', 'order', 'text')
    list_filter = ('mission',)
    search_fields = ('text',)
    inlines = [ChoiceInline]

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score', 'current_mission')
    list_filter = ('completed_missions',)
    search_fields = ('user__username',)

@admin.register(PlayerAnswer)
class PlayerAnswerAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'get_is_correct', 'get_answer_date')
    list_filter = ('question__mission',)
    search_fields = ('player__user__username',)

    def get_is_correct(self, obj):
        """Return whether the answer is correct"""
        return obj.is_correct
    get_is_correct.short_description = 'Correct?'
    get_is_correct.boolean = True

    def get_answer_date(self, obj):
        """Return the timestamp in a formatted way"""
        return obj.timestamp
    get_answer_date.short_description = 'Answered On'
    get_answer_date.admin_order_field = 'timestamp'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct', 'question__mission')
    search_fields = ('text',)