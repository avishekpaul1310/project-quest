from django.core.management.base import BaseCommand
from game.models import Mission, Question

class Command(BaseCommand):
    help = 'Creates sample missions and questions for Project Quest'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing missions and questions...')
        Mission.objects.all().delete()
        
        # Mission 1
        self.stdout.write('Creating Mission 1...')
        mission1 = Mission.objects.create(
            title="Project Management Fundamentals",
            description="Learn the basic concepts of project management and key terminology.",
            order=1,
            xp_reward=100,
            content="Welcome to Project Management Fundamentals!",
            objective="Understand core project management concepts",
            key_concepts="Project definition, Project lifecycle, Project manager role",
            best_practices="Follow PMI standards and best practices",
            npc_name="Master Project Manager",
            npc_dialogue="Welcome, apprentice! Let's begin your journey into project management."
        )

        Question.objects.create(
            mission=mission1,
            scenario="What is a project?",  # Changed from text to scenario
            option_a="A routine operational task",
            option_b="A temporary endeavor undertaken to create a unique product, service, or result",
            option_c="A permanent organizational process",
            option_d="A continuous business operation",
            correct_option="B",
            explanation="A project is temporary and unique, unlike routine operational work."
        )

        # Mission 2
        self.stdout.write('Creating Mission 2...')
        mission2 = Mission.objects.create(
            title="Project Planning Essentials",
            description="Master the art of project planning and scheduling.",
            order=2,
            xp_reward=150,
            content="Welcome to Project Planning Essentials!",
            objective="Learn essential project planning techniques",
            key_concepts="WBS, Schedule Development, Resource Planning",
            best_practices="Progressive elaboration, Rolling wave planning",
            npc_name="Planning Sage",
            npc_dialogue="Planning is the key to project success. Let me show you how!"
        )

        Question.objects.create(
            mission=mission2,
            scenario="What is a Work Breakdown Structure (WBS)?",  # Changed from text to scenario
            option_a="A team organization chart",
            option_b="A decomposition of project work into smaller components",
            option_c="A project budget document",
            option_d="A risk management plan",
            correct_option="B",
            explanation="WBS breaks down project work into manageable components."
        )

        # Mission 3
        self.stdout.write('Creating Mission 3...')
        mission3 = Mission.objects.create(
            title="Stakeholder Management",
            description="Learn how to identify and manage project stakeholders effectively.",
            order=3,
            xp_reward=200,
            content="Welcome to Stakeholder Management!",
            objective="Master stakeholder management techniques",
            key_concepts="Stakeholder identification, Analysis, Communication",
            best_practices="Regular stakeholder engagement, Clear communication",
            npc_name="Stakeholder Guru",
            npc_dialogue="Understanding your stakeholders is crucial for project success!"
        )

        Question.objects.create(
            mission=mission3,
            scenario="What is the first step in stakeholder management?",  # Changed from text to scenario
            option_a="Create a communication plan",
            option_b="Identify stakeholders",
            option_c="Hold a kickoff meeting",
            option_d="Develop project charter",
            correct_option="B",
            explanation="Identifying stakeholders is the first step in effective stakeholder management."
        )

        self.stdout.write(self.style.SUCCESS('Successfully created sample missions and questions!'))