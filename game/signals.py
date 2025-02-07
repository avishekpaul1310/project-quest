from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerProfile, Mission

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    """Create PlayerProfile for new users only if one doesn't exist"""
    if created:
        # Check if a profile already exists
        if not PlayerProfile.objects.filter(user=instance).exists():
            # Get first mission before creating profile
            first_mission = Mission.objects.filter(is_active=True).order_by('order').first()
            # Create profile with first mission
            PlayerProfile.objects.create(
                user=instance,
                current_mission=first_mission
            )

@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    """Save PlayerProfile if it exists"""
    if hasattr(instance, 'playerprofile'):
        instance.playerprofile.save()