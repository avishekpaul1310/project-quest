from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('order', models.IntegerField(unique=True)),
                ('key_concepts', models.TextField()),
                ('best_practices', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='The question text')),
                ('order', models.IntegerField(help_text='Order of question within the mission')),
                ('explanation', models.TextField(help_text='Explanation shown after answering')),
                ('mission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='game.mission')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PlayerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('current_mission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game.mission')),
                ('completed_missions', models.ManyToManyField(blank=True, related_name='completed_by', to='game.mission')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='The choice text')),
                ('is_correct', models.BooleanField(default=False, help_text='Whether this is the correct answer')),
                ('explanation', models.TextField(blank=True, help_text='Explanation why this choice is correct/incorrect')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='game.question')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.playerprofile')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.question')),
                ('selected_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.choice')),
            ],
            options={
                'unique_together': {('player', 'question')},
            },
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(fields=('mission', 'order'), name='unique_question_order_per_mission'),
        ),
    ]