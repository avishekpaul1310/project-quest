from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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

class Question(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField()
    explanation = models.TextField()

    class Meta:
        ordering = ['order']
        unique_together = ['mission', 'order']

    def __str__(self):
        return f"Question {self.order} for {self.mission.title}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Choice for {self.question}: {self.text[:50]}"

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    completed_missions = models.ManyToManyField(Mission, blank=True, related_name='completed_by')
    total_score = models.IntegerField(default=0)
    current_mission = models.ForeignKey(
        Mission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_players'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def can_access_mission(self, mission):
        if mission.order == 1:
            return True
        prev_mission = Mission.objects.filter(
            is_active=True,
            order=mission.order - 1
        ).first()
        return prev_mission and self.completed_missions.filter(id=prev_mission.id).exists()
    
class PlayerAnswer(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['player', 'question']

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    """Create PlayerProfile for new users only if one doesn't exist"""
    if created and not hasattr(instance, 'playerprofile'):
        PlayerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    """Save PlayerProfile if it exists"""
    if hasattr(instance, 'playerprofile'):
        instance.playerprofile.save()