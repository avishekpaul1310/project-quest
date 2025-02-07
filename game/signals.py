from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerProfile, Mission

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    if created:  # Only try to create a profile if this is a new user
        # Get the first mission (ordered by 'order' field)
        first_mission = Mission.objects.filter(is_active=True).order_by('order').first()
        # Use get_or_create instead of create to avoid duplicate profiles
        PlayerProfile.objects.get_or_create(
            user=instance,
            defaults={'current_mission': first_mission}
        )

@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    # Only save if the profile exists
    if hasattr(instance, 'playerprofile'):
        instance.playerprofile.save()