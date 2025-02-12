from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

class ModelTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test mission
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )

    def test_mission_creation(self):
        """Test mission can be created"""
        self.assertEqual(self.mission.title, 'Test Mission')
        self.assertEqual(self.mission.order, 1)

    def test_player_profile_creation(self):
        """Test player profile is created automatically"""
        profile = PlayerProfile.objects.get(user=self.user)
        self.assertEqual(profile.total_score, 0)
        self.assertEqual(profile.current_mission_id, 1)

    def test_mission_access(self):
        """Test mission access rules"""
        profile = PlayerProfile.objects.get(user=self.user)
        self.assertTrue(profile.can_access_mission(self.mission))