from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.transaction import atomic
from .models import PlayerProfile, Mission

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    """Create PlayerProfile for new users only if one doesn't exist"""
    if created:
        with atomic():
            # Get first mission before creating profile
            first_mission = Mission.objects.filter(is_active=True).order_by('order').first()
            # Create profile with first mission
            if not PlayerProfile.objects.filter(user=instance).exists():
                PlayerProfile.objects.create(
                    user=instance,
                    current_mission=first_mission
                )