from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
import logging

logger = logging.getLogger(__name__)

class ModelTests(TestCase):
    def setUp(self):
        # Create test missions first
        self.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='• Project charter defines project\n• Authorizes project formally',
            best_practices='• Align with business goals\n• Identify stakeholders early',
            is_active=True
        )
        logger.debug(f"Created mission1: {self.mission1}")
        
        self.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='• Identify stakeholders\n• Analyze their interests',
            best_practices='• Regular communication\n• Address concerns early',
            is_active=True
        )
        logger.debug(f"Created mission2: {self.mission2}")

        # Create test user after missions exist
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        logger.debug(f"Created user: {self.user.username}")
        
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
        # Verify profile exists
        self.assertTrue(hasattr(self.user, 'playerprofile'))
        profile = self.user.playerprofile
        logger.debug(f"Profile for user {self.user.username}: {profile}")
        logger.debug(f"Profile's current mission: {profile.current_mission}")
        logger.debug(f"Expected mission: {self.mission1}")
        
        # Verify initial values
        self.assertEqual(profile.total_score, 0)
        self.assertEqual(profile.current_mission, self.mission1)