from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerProfile, Mission

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    if created:
        # Get the first mission (ordered by 'order' field)
        first_mission = Mission.objects.filter(is_active=True).order_by('order').first()
        PlayerProfile.objects.create(user=instance, current_mission=first_mission)

@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    instance.playerprofile.save()