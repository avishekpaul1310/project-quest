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
            # Create profile if it doesn't exist
            profile, created = PlayerProfile.objects.get_or_create(
                user=instance
            )

@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    """Save PlayerProfile if it exists"""
    if hasattr(instance, 'playerprofile'):
        instance.playerprofile.save()