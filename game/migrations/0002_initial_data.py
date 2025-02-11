from django.db import migrations

def create_initial_data(apps, schema_editor):
    Mission = apps.get_model('game', 'Mission')
    Question = apps.get_model('game', 'Question')
    Choice = apps.get_model('game', 'Choice')

    # Create Mission 1
    mission1 = Mission.objects.create(
        title="Introduction to Project Management",
        order=1,
        key_concepts="""
        • Project charter formally authorizes a project
        • Defines project objectives and scope
        • Identifies key stakeholders
        """,
        best_practices="""
        • Ensure alignment with business goals
        • Get stakeholder buy-in early
        • Keep documentation clear and concise
        """
    )

    # Create a sample question
    question1 = Question.objects.create(
        mission=mission1,
        text="What is the primary purpose of a project charter?",
        order=1,
        explanation="A project charter formally authorizes the project and provides the project manager with authority."
    )

    Choice.objects.create(
        question=question1,
        text="To formally authorize the project and assign the project manager",
        is_correct=True,
        explanation="Correct! The project charter formally authorizes the project and assigns the project manager."
    )

    Choice.objects.create(
        question=question1,
        text="To create a detailed project schedule",
        is_correct=False,
        explanation="Incorrect. Project schedules are created during project planning, not in the charter."
    )

def reverse_migrations(apps, schema_editor):
    Mission = apps.get_model('game', 'Mission')
    Mission.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_migrations),
    ]