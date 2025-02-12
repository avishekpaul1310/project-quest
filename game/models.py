from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    completed_missions = models.ManyToManyField('Mission', blank=True, related_name='completed_by')
    current_mission_id = models.IntegerField(default=1)  # Added missing field
    
    class Meta:
        ordering = ['-total_score']

    def update_score(self, points):
        self.total_score += points
        self.save()
    
    def get_mission_progress(self, mission):
        total_questions = mission.questions.count()
        answered = PlayerAnswer.objects.filter(player=self, question__mission=mission)
        correct = answered.filter(selected_choice__is_correct=True)
        return {
            'total_questions': total_questions,
            'answered_questions': answered.count(),
            'correct_answers': correct.count(),
            'completed': self.has_completed_mission(mission)
        }

    def complete_mission(self, mission):
        if not self.has_completed_mission(mission):
            progress = self.get_mission_progress(mission)
            if progress['correct_answers'] >= progress['total_questions'] * 0.7:
                self.completed_missions.add(mission)
                self.update_score(50)  # Fixed score value
                self.current_mission_id = mission.order + 1
                self.save()
                return True
        return False
    
class Mission(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(unique=True)
    key_concepts = models.TextField(blank=True)
    best_practices = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Mission {self.order}: {self.title}"  # Fixed string representation

class Question(models.Model):
    mission = models.ForeignKey(Mission, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.IntegerField()
    explanation = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['mission', 'order']
    
    def clean(self):
        if self.pk and not self.choices.filter(is_correct=True).exists():
            raise ValidationError('Question must have at least one correct answer.')

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField()
    
    def clean(self):
        if self.is_correct and self.question.choices.exclude(id=self.id).filter(is_correct=True).exists():
            raise ValidationError('Only one choice can be correct per question')
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class PlayerAnswer(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['player', 'question']