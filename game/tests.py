from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class ModelTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test missions
        self.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='• Project charter defines project\n• Authorizes project formally',
            best_practices='• Align with business goals\n• Identify stakeholders early',
            is_active=True
        )
        
        self.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='• Identify stakeholders\n• Analyze their interests',
            best_practices='• Regular communication\n• Address concerns early',
            is_active=True
        )
        
        # Create test questions for mission 1
        self.question1 = Question.objects.create(
            mission=self.mission1,
            text='What is a project charter?',
            order=1,
            explanation='A project charter formally authorizes the project.'
        )
        
        # Create choices for question 1
        self.choice1_correct = Choice.objects.create(
            question=self.question1,
            text='A document that formally authorizes the project',
            is_correct=True
        )
        self.choice1_wrong = Choice.objects.create(
            question=self.question1,
            text='A project schedule',
            is_correct=False
        )

    def test_player_profile_creation(self):
        """Test that PlayerProfile is created automatically for new users"""
        self.assertTrue(hasattr(self.user, 'playerprofile'))
        self.assertEqual(self.user.playerprofile.total_score, 0)
        self.assertEqual(self.user.playerprofile.current_mission, self.mission1)

    def test_mission_access(self):
        """Test mission access logic"""
        profile = self.user.playerprofile
        
        # User should be able to access Mission 1
        self.assertTrue(profile.can_access_mission(self.mission1))
        
        # User should not be able to access Mission 2 yet
        self.assertFalse(profile.can_access_mission(self.mission2))
        
        # After completing Mission 1, user should be able to access Mission 2
        profile.completed_missions.add(self.mission1)
        self.assertTrue(profile.can_access_mission(self.mission2))

    def test_question_uniqueness(self):
        """Test that questions must have unique order within a mission"""
        with self.assertRaises(Exception):
            Question.objects.create(
                mission=self.mission1,
                text='Duplicate order question',
                order=1,  # This should fail as order=1 already exists
                explanation='This should not be created'
            )

    def test_mission_ordering(self):
        """Test that missions are returned in correct order"""
        missions = Mission.objects.all()
        self.assertEqual(missions[0], self.mission1)
        self.assertEqual(missions[1], self.mission2)

class PlayerProgressTests(TestCase):
    def setUp(self):
        # Create mission first
        self.mission = Mission.objects.create(
            title='Test Mission',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        # Create test user after mission exists
        self.user = User.objects.create_user(
            username='testplayer',
            password='testpass123'
        )
        
        self.question = Question.objects.create(
            mission=self.mission,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct answer',
            is_correct=True
        )
        
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text='Wrong answer',
            is_correct=False
        )

    def test_answer_recording(self):
        """Test that player answers are recorded correctly"""
        profile = self.user.playerprofile
        
        # Record a correct answer
        answer = PlayerAnswer.objects.create(
            player=profile,
            question=self.question,
            selected_choice=self.correct_choice,
            is_correct=True
        )
        
        # Check that the answer was recorded
        self.assertTrue(
            PlayerAnswer.objects.filter(
                player=profile,
                question=self.question,
                is_correct=True
            ).exists()
        )
        
        # Try to record another answer for the same question (should raise an error)
        with self.assertRaises(Exception):
            PlayerAnswer.objects.create(
                player=profile,
                question=self.question,
                selected_choice=self.wrong_choice,
                is_correct=False
            )

    def test_mission_completion(self):
        """Test mission completion logic"""
        profile = self.user.playerprofile
        
        # Initially, mission should not be completed
        self.assertFalse(profile.completed_missions.filter(id=self.mission.id).exists())
        
        # Add mission to completed missions
        profile.completed_missions.add(self.mission)
        
        # Check that mission is now marked as completed
        self.assertTrue(profile.completed_missions.filter(id=self.mission.id).exists())