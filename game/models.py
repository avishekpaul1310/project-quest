from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    title = models.CharField(max_length=100, default="Apprentice Project Manager")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Mission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # New fields for enhanced mission content
    objective = models.TextField(help_text="Main objective of the mission")
    key_concepts = models.TextField(help_text="Key PM concepts to learn in this mission")
    best_practices = models.TextField(help_text="Best practices for the mission")
    npc_name = models.CharField(max_length=100, help_text="Name of the NPC giving the mission")
    npc_dialogue = models.TextField(help_text="Dialogue from the NPC")
    xp_reward = models.IntegerField(default=100, help_text="XP points awarded for completing the mission")
    
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Question(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    scenario = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    def get_options(self):
        """Returns a list of tuples with option letters and their corresponding text."""
        return [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d)
        ]
    
    explanation = models.TextField(help_text="Explanation for the correct answer")
    
    def __str__(self):
        return f"Question for {self.mission.title}"

class UserMissionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'mission']
    
    def __str__(self):
        return f"{self.user.username} - {self.mission.title}"