from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
import logging

logger = logging.getLogger(__name__)

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified data for all class methods"""
        # Create test missions first
        cls.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        cls.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='Test concepts 2',
            best_practices='Test practices 2',
            is_active=True
        )

    def setUp(self):
        """Set up data for each test method"""
        # Create a new user for each test
        self.user = User.objects.create_user(
            username=f'testuser_{self._testMethodName}',  # Make username unique for each test
            password='testpass123'
        )
        # Profile is created automatically via signal
        self.profile = PlayerProfile.objects.get(user=self.user)

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