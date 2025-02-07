from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
import logging

logger = logging.getLogger(__name__)

class ModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test missions
        self.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        self.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='Test concepts 2',
            best_practices='Test practices 2',
            is_active=True
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Get the automatically created profile
        self.profile = self.user.playerprofile

    def test_mission_access(self):
        """Test mission access logic"""
        # User should be able to access Mission 1
        self.assertTrue(self.profile.can_access_mission(self.mission1))
        
        # User should not be able to access Mission 2 yet
        self.assertFalse(self.profile.can_access_mission(self.mission2))
        
        # After completing Mission 1, user should be able to access Mission 2
        self.profile.completed_missions.add(self.mission1)
        self.assertTrue(self.profile.can_access_mission(self.mission2))

    def test_mission_creation(self):
        """Test mission creation and attributes"""
        self.assertEqual(self.mission1.title, 'Project Charter Basics')
        self.assertEqual(self.mission1.order, 1)
        self.assertTrue(self.mission1.is_active)

    def test_mission_ordering(self):
        """Test that missions are returned in correct order"""
        missions = Mission.objects.filter(is_active=True).order_by('order')
        self.assertEqual(missions[0], self.mission1)
        self.assertEqual(missions[1], self.mission2)

    def test_player_profile_creation(self):
        """Test that PlayerProfile is created automatically for new users"""
        self.assertTrue(hasattr(self.user, 'playerprofile'))
        self.assertEqual(self.profile.total_score, 0)
        self.assertEqual(self.profile.current_mission, self.mission1)

    def test_question_uniqueness(self):
        """Test that questions must have unique order within a mission"""
        Question.objects.create(
            mission=self.mission1,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        
        # Try to create another question with the same order in the same mission
        with self.assertRaises(Exception):
            Question.objects.create(
                mission=self.mission1,
                text='Another question',
                order=1,
                explanation='This should fail'
            )

class PlayerProgressTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test mission
        self.mission = Mission.objects.create(
            title='Test Mission',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testplayer',
            password='testpass123'
        )
        
        # Get the automatically created profile
        self.profile = self.user.playerprofile
        
        # Create test question
        self.question = Question.objects.create(
            mission=self.mission,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        
        # Create choices
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

class ViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test missions
        self.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        self.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='Test concepts 2',
            best_practices='Test practices 2',
            is_active=True
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Get the automatically created profile
        self.profile = self.user.playerprofile
        
        # Create the test client
        self.client = Client()