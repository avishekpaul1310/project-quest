from django.db import migrations
from django.core.management import call_command

def load_initial_data(apps, schema_editor):
    # Load missions first
    call_command('loaddata', 'initial_data.json')
    # Then load questions and choices
    call_command('loaddata', 'questions.json')

def reverse_initial_data(apps, schema_editor):
    Mission = apps.get_model('game', 'Mission')
    Question = apps.get_model('game', 'Question')
    Choice = apps.get_model('game', 'Choice')
    
    Choice.objects.all().delete()
    Question.objects.all().delete()
    Mission.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0003_remove_playeranswer_is_correct'),
    ]

    operations = [
        migrations.RunPython(load_initial_data, reverse_initial_data),
    ]