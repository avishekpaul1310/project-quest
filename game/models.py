from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    completed_missions = models.ManyToManyField('Mission', blank=True, related_name='completed_by')
    
    class Meta:
        ordering = ['-total_score']
    
    def update_score(self, points):
        """Update player's score"""
        self.total_score += points
        self.save()
    
    def complete_mission(self, mission):
        """Complete a mission and update score"""
        if not self.has_completed_mission(mission):
            correct_answers = PlayerAnswer.objects.filter(
                player=self,
                question__mission=mission,
                selected_choice__is_correct=True
            ).count()
            total_questions = mission.questions.count()
            score = (correct_answers / total_questions) * 100
            if score >= 70:  # Pass threshold
                self.completed_missions.add(mission)
                self.update_score(int(score))
                return True
        return False

    def has_completed_mission(self, mission):
        """Check if user has completed a specific mission"""
        return mission in self.completed_missions.all()

    def can_access_mission(self, mission):
        """Check if user can access a mission"""
        if mission.order == 1:
            return True
        prev_mission = Mission.objects.filter(order=mission.order - 1).first()
        return prev_mission and self.has_completed_mission(prev_mission)

class Mission(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(unique=True)
    key_concepts = models.TextField(blank=True)
    best_practices = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
    
    def clean(self):
        if self.pk and self.questions.count() != 5:
            raise ValidationError('Each mission must have exactly 5 questions.')
    
    def __str__(self):
        return self.title

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
    explanation = models.TextField()  # Required field for feedback
    
    def save(self, *args, **kwargs):
        if not self.explanation:
            self.explanation = "Generic explanation for this choice."
        super().save(*args, **kwargs)

class PlayerAnswer(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['player', 'question']