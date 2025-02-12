from django.db import migrations, models

def combine_fields(apps, schema_editor):
    Mission = apps.get_model('game', 'Mission')
    for mission in Mission.objects.all():
        # Combine key_concepts and best_practices into description
        mission.description = f"Key Concepts:\n{mission.key_concepts}\n\nBest Practices:\n{mission.best_practices}"
        mission.save()

class Migration(migrations.Migration):

    dependencies = [
        ('game', 'XXXX_previous_migration'),  # Replace with your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='Mission',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.RunPython(combine_fields),
        migrations.RemoveField(
            model_name='Mission',
            name='key_concepts',
        ),
        migrations.RemoveField(
            model_name='Mission',
            name='best_practices',
        ),
    ]