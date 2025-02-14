# Generated by Django 5.1.5 on 2025-02-14 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_alter_question_correct_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='objectives',
            field=models.TextField(blank=True, default='', help_text='Mission objectives (one per line)'),
        ),
        migrations.AddField(
            model_name='mission',
            name='topics',
            field=models.TextField(blank=True, default='', help_text='Topics covered in this mission (one per line)'),
        ),
    ]
