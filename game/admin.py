from django.contrib import admin
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'get_mission_status')
    search_fields = ('title',)
    
    def get_mission_status(self, obj):
        # A mission is considered active if it has exactly 5 questions
        return obj.questions.count() == 5
    get_mission_status.short_description = 'Active'
    get_mission_status.boolean = True

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('mission', 'order', 'text')
    list_filter = ('mission',)
    search_fields = ('text',)
    inlines = [ChoiceInline]

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score', 'get_current_mission')
    list_filter = ('completed_missions',)
    search_fields = ('user__username',)
    
    def get_current_mission(self, obj):
        mission_id = obj.current_mission_id
        if mission_id:
            try:
                mission = Mission.objects.get(id=mission_id)
                return f"Mission {mission.order}: {mission.title}"
            except Mission.DoesNotExist:
                return "No mission found"
        return "All missions completed"
    get_current_mission.short_description = 'Current Mission'

@admin.register(PlayerAnswer)
class PlayerAnswerAdmin(admin.ModelAdmin):
    list_display = ('player', 'question', 'get_is_correct', 'get_answer_date')
    list_filter = ('question__mission',)
    search_fields = ('player__user__username',)

    def get_is_correct(self, obj):
        """Return whether the answer is correct"""
        return obj.selected_choice.is_correct
    get_is_correct.short_description = 'Correct?'
    get_is_correct.boolean = True

    def get_answer_date(self, obj):
        """Return the timestamp in a formatted way"""
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    get_answer_date.short_description = 'Answered On'
    get_answer_date.admin_order_field = 'timestamp'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct', 'question__mission')
    search_fields = ('text',)