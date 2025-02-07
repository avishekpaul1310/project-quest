from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerProfile, Mission

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    """Create PlayerProfile when a new User is created"""
    if created:
        # Get the first mission before creating the profile
        first_mission = Mission.objects.filter(is_active=True).order_by('order').first()
        # Create the profile with the first mission
        PlayerProfile.objects.create(
            user=instance,
            current_mission=first_mission,
            total_score=0
        )