from django.db import migrations, models

def combine_fields(apps, schema_editor):
    Mission = apps.get_model('game', 'Mission')
    for mission in Mission.objects.all():
        # Since description field already exists (renamed from best_practices),
        # we'll just cleanup and standardize the format
        mission.description = mission.description
        mission.save()

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0007_alter_mission_options_and_more'),
    ]

    operations = [
        migrations.RunPython(combine_fields, reverse_code=migrations.RunPython.noop),
    ]