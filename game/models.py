from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError

class Mission(models.Model):
    title = models.CharField(max_length=200)
    order = models.IntegerField(unique=True)
    key_concepts = models.TextField()
    best_practices = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Mission {self.order}: {self.title}"
    
    def clean(self):
        """Ensure mission has exactly 5 questions"""
        if self.questions.count() != 5:
            raise ValidationError("Each mission must have exactly 5 questions.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Question(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text="The question text")
    order = models.IntegerField(help_text="Order of question within the mission")
    explanation = models.TextField(help_text="Explanation shown after answering")
    
    class Meta:
        unique_together = ['mission', 'order']
        ordering = ['order']

    def __str__(self):
        return f"Mission {self.mission.order}, Q{self.order}: {self.text[:50]}..."

    def is_answered_correctly_by(self, player):
        """Check if the player answered this question correctly"""
        try:
            answer = PlayerAnswer.objects.get(player=player, question=self)
            return answer.selected_choice.is_correct
        except PlayerAnswer.DoesNotExist:
            return False

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField(help_text="The choice text")
    is_correct = models.BooleanField(default=False, help_text="Whether this is the correct answer")
    explanation = models.TextField(help_text="Explanation why this choice is correct/incorrect", blank=True)

    def __str__(self):
        return f"{self.text[:50]}... ({'✓' if self.is_correct else '✗'})"

    def save(self, *args, **kwargs):
        if self.is_correct:
            # Ensure only one correct answer per question
            self.question.choices.exclude(id=self.id).update(is_correct=False)
        super().save(*args, **kwargs)
        
class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_mission = models.ForeignKey(Mission, on_delete=models.SET_NULL, null=True, blank=True)
    total_score = models.IntegerField(default=0)
    completed_missions = models.ManyToManyField(Mission, related_name='completed_by', blank=True)

    def can_access_mission(self, mission):
        if mission.id == 1:
            return True
        previous_mission = Mission.objects.filter(id=mission.id - 1).first()
        return previous_mission in self.completed_missions.all()

class PlayerAnswer(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['player', 'question'] 
    def __str__(self):
        return f"{self.player.user.username}'s answer to {self.question}"

    @property
    def is_correct(self):
        """Check if the selected answer is correct"""
        return self.selected_choice.is_correct

    def save(self, *args, **kwargs):
        if self.pk:  # If this is an update
            old_answer = PlayerAnswer.objects.get(pk=self.pk)
            # Remove points for old answer if it was correct
            if old_answer.selected_choice.is_correct:
                self.player.add_score(-10)
        # Add points for new correct answer
        if self.selected_choice.is_correct:
            self.player.add_score(10)
        super().save(*args, **kwargs)