from django.db import models
from django.contrib.auth.models import User

class Mission(models.Model):
    title = models.CharField(max_length=200)
    order = models.IntegerField(unique=True)
    key_concepts = models.TextField(help_text="Key concepts in bullet points")
    best_practices = models.TextField(help_text="Practical tips for applying concepts")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Mission {self.order}: {self.title}"

class Question(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField()
    explanation = models.TextField(help_text="Explanation shown for wrong answers")
    
    class Meta:
        ordering = ['order']
        unique_together = ['mission', 'order']
        
    def __str__(self):
        return f"{self.mission.title} - Question {self.order}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question} - {self.text[:30]}"

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
    
    def save(self, *args, **kwargs):
        # If this is a new profile (no ID) and no current_mission is set
        if not self.pk and not self.current_mission:
            # Set the first active mission as current_mission
            first_mission = Mission.objects.filter(is_active=True).order_by('order').first()
            self.current_mission = first_mission
        super().save(*args, **kwargs)
    
    def can_access_mission(self, mission):
        """
        Determine if the user can access a given mission.
        Rules:
        1. Mission 1 is always accessible
        2. Other missions are accessible only if the previous mission is completed
        """
        # First mission is always accessible
        if mission.order == 1:
            return True
            
        # Find the previous mission
        prev_mission = Mission.objects.filter(
            is_active=True,
            order=mission.order - 1
        ).first()
        
        # If there's no previous mission (shouldn't happen) or if it's completed
        if not prev_mission:
            return False
            
        return self.completed_missions.filter(id=prev_mission.id).exists()

class PlayerAnswer(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    
    class Meta:
        unique_together = ['player', 'question']