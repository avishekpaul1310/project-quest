from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    xp_points = models.IntegerField(default=0)
    title = models.CharField(max_length=100, default="Apprentice Project Manager")
    session_id = models.CharField(max_length=100, blank=True, null=True)
    last_session_start = models.DateTimeField(null=True, blank=True)

    def start_new_session(self):
        """Start a new game session"""
        # Reset progress
        self.total_score = 0
        self.xp_points = 0
        self.title = "Apprentice Project Manager"
        self.session_id = f"session_{timezone.now().timestamp()}"
        self.last_session_start = timezone.now()
        self.save()
        
        # Clear previous mission progress
        UserMissionProgress.objects.filter(user=self.user).delete()

    def reset_progress(self):
        """Reset user's progress"""
        self.total_score = 0
        self.xp_points = 0
        self.title = "Apprentice Project Manager"
        self.session_id = None
        self.last_session_start = None
        self.save()
        
        # Clear mission progress
        UserMissionProgress.objects.filter(user=self.user).delete()
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class Mission(models.Model):
    MISSION_LEVELS = [
        ('VILLAGE', '🏡 Village Management'),
        ('TRADE', '🛍️ Trade Route Management'),
        ('CASTLE', '🏰 Castle Management'),
        ('TOURNAMENT', '🎯 Tournament Management')
    ]

    # Basic Information
    title = models.CharField(max_length=255)
    mission_type = models.CharField(max_length=20, choices=MISSION_LEVELS)
    story_title = models.CharField(max_length=255)
    
    # Make these fields optional by adding null=True, blank=True
    description = models.TextField(null=True, blank=True)
    pmbok_chapter = models.CharField(max_length=255, null=True, blank=True)
    key_concepts = models.TextField(null=True, blank=True)
    best_practices = models.TextField(null=True, blank=True)
    npc_dialogue = models.TextField(null=True, blank=True)
    objective = models.TextField(null=True, blank=True)
    pm_concepts = models.CharField(max_length=255, null=True, blank=True)
    
    # Gamification
    xp_reward = models.IntegerField(default=100)
    order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_mission_type_display()}: {self.title}"
    
class Question(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='questions')
    scenario_title = models.CharField(max_length=255)
    scenario = models.TextField()
    text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    explanation = models.TextField()
    consequence_a = models.TextField()
    consequence_b = models.TextField()
    consequence_c = models.TextField()
    consequence_d = models.TextField()

    def __str__(self):
        return f"{self.scenario_title} - {self.mission.title}"

class UserMissionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'mission']