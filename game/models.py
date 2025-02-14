from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Mission(models.Model):
    MISSION_TYPES = [
        ('VILLAGE_FESTIVAL', 'Village Festival'),
        ('TRADE_ROUTE', 'Trade Route'),
        ('CASTLE_RESTORATION', 'Castle Restoration'),
        ('GRAND_TOURNAMENT', 'Grand Tournament'),
    ]

    title = models.CharField(max_length=200)
    story_title = models.CharField(max_length=200)
    description = models.TextField()
    mission_type = models.CharField(max_length=50, choices=MISSION_TYPES)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    xp_reward = models.IntegerField(default=100)
    
    # Learning Content Fields - all with explicit defaults and blank=True
    
    objectives = models.TextField(
        help_text="Mission objectives (one per line)",
        default="",
        blank=True
    )
    
    topics = models.TextField(
        help_text="Topics covered in this mission (one per line)",
        default="",
        blank=True
    )
    
    key_concepts = models.TextField(
        help_text="Key project management concepts for this mission",
        default='',
        blank=True,
        null=True  # Adding null=True to handle existing records
    )
    
    best_practices = models.TextField(
        help_text="Best practices applied to this mission",
        default='',
        blank=True,
        null=True  # Adding null=True to handle existing records
    )
    
    npc_dialogue = models.TextField(
        help_text="NPC dialogue introducing the mission",
        default='',
        blank=True,
        null=True  # Adding null=True to handle existing records
    )

    def __str__(self):
        return f"{self.story_title} ({self.title})"

    class Meta:
        ordering = ['order']

class Question(models.Model):
    CORRECT_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    scenario_title = models.CharField(max_length=200)
    scenario = models.TextField()
    text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=CORRECT_CHOICES,
        help_text="Select the correct option (A, B, C, or D)"
    )
    explanation = models.TextField()
    consequence_a = models.TextField()
    consequence_b = models.TextField()
    consequence_c = models.TextField()
    consequence_d = models.TextField()

    def __str__(self):
        return f"{self.mission.story_title} - {self.scenario_title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    xp_points = models.IntegerField(default=0)
    title = models.CharField(max_length=100, default="Apprentice Project Manager")
    session_id = models.CharField(max_length=100, blank=True, null=True)
    last_session_start = models.DateTimeField(null=True, blank=True)

    def start_new_session(self):
        """Start a new game session"""
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

    def __str__(self):
        return f"{self.user.username}'s Profile"

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