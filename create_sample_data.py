# Save this as create_sample_data.py in your project root
from django.core.management.base import BaseCommand
from game.models import Mission, Question

def create_sample_data():
    # Mission 1: Project Management Basics
    mission1 = Mission.objects.create(
        title="Project Management Fundamentals",
        description="Learn the basic concepts of project management and key terminology.",
        order=1,
        xp_reward=100,
        content="""
        Welcome to Project Management Fundamentals!
        
        In this mission, you'll learn about:
        1. What is a project?
        2. Project lifecycle
        3. Role of a project manager
        4. Project constraints (Time, Cost, Scope)
        """
    )

    Question.objects.create(
        mission=mission1,
        text="What is a project?",
        option_a="A routine operational task",
        option_b="A temporary endeavor undertaken to create a unique product, service, or result",
        option_c="A permanent organizational process",
        option_d="A continuous business operation",
        correct_option="B",
        explanation="A project is temporary and unique, unlike routine operational work."
    )

    # Mission 2: Project Planning
    mission2 = Mission.objects.create(
        title="Project Planning Essentials",
        description="Master the art of project planning and scheduling.",
        order=2,
        xp_reward=150,
        content="""
        Welcome to Project Planning Essentials!
        
        Key topics covered:
        1. Work Breakdown Structure (WBS)
        2. Project Schedule Development
        3. Resource Planning
        4. Risk Management Basics
        """
    )

    Question.objects.create(
        mission=mission2,
        text="What is a Work Breakdown Structure (WBS)?",
        option_a="A team organization chart",
        option_b="A decomposition of project work into smaller components",
        option_c="A project budget document",
        option_d="A risk management plan",
        correct_option="B",
        explanation="WBS breaks down project work into manageable components."
    )

    print("Sample missions and questions created successfully!")

# To run this script:
if __name__ == "__main__":
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_quest.settings')
    django.setup()
    create_sample_data()