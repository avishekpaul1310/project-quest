from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerProfile, Mission
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    """Create PlayerProfile when a new User is created"""
    if created:
        # Get the first mission before creating the profile
        first_mission = Mission.objects.filter(is_active=True).order_by('order').first()
        logger.debug(f"Found first mission: {first_mission}")
        
        # Create the profile
        profile = PlayerProfile.objects.create(user=instance)
        logger.debug(f"Created profile for user: {instance.username}")
        
        # Set the current mission
        profile.current_mission = first_mission
        profile.save()
        logger.debug(f"Updated profile with current_mission: {first_mission}")