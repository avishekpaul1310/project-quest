from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Mission(models.Model):
    title = models.CharField(max_length=200)
    order = models.IntegerField(unique=True)
    description = models.TextField()

    class Meta:
        ordering = ['order']
        verbose_name = 'Mission'
        verbose_name_plural = 'Missions'

    def __str__(self):
        return f"Mission {self.order}: {self.title}"

    def clean(self):
        if not self._state.adding:
            question_count = self.questions.count()
            if question_count != 5:
                raise ValidationError('Mission must have exactly 5 questions')
            
            for question in self.questions.all():
                if not question.choices.filter(is_correct=True).exists():
                    raise ValidationError(f'Question "{question.text}" must have at least one correct answer')

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        if not creating:
            self.full_clean()
            
    def get_next_mission(self):
        return Mission.objects.filter(order__gt=self.order).order_by('order').first()

    def get_previous_mission(self):
        return Mission.objects.filter(order__lt=self.order).order_by('-order').first()
    
class Question(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text='The question text')
    order = models.IntegerField(help_text='Order of question within the mission')
    explanation = models.TextField(help_text='Explanation shown after answering')

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['mission', 'order'], 
                                  name='unique_question_order_per_mission')
        ]

    def __str__(self):
        return f"Question {self.order} for {self.mission}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField()

    def clean(self):
        # Ensure only one correct answer per question
        if self.is_correct:
            existing_correct = Choice.objects.filter(
                question=self.question,
                is_correct=True
            ).exclude(id=self.id)
            
            if existing_correct.exists():
                raise ValidationError('Only one choice can be marked as correct')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    completed_missions = models.ManyToManyField(Mission, blank=True)

    def can_access_mission(self, mission):
        """Check if user can access a mission"""
        if mission.order == 1:
            return True
            
        # Get previous mission
        prev_mission = Mission.objects.filter(order=mission.order - 1).first()
        if not prev_mission:
            return False
            
        return prev_mission in self.completed_missions.all()

    def get_mission_progress(self, mission):
        """Get progress for a specific mission"""
        answers = PlayerAnswer.objects.filter(
            player=self,
            question__mission=mission
        )
        total_questions = mission.questions.count()
        correct_answers = answers.filter(selected_choice__is_correct=True).count()
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'is_completed': mission in self.completed_missions.all()
        }

class PlayerAnswer(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['player', 'question']

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    if created:
        PlayerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    instance.playerprofile.save()