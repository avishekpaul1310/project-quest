from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class ModelTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test mission
        self.mission = Mission.objects.create(
            title="Test Mission",
            order=1,
            key_concepts="Test concepts",
            best_practices="Test practices"
        )
        
        # Create test question
        self.question = Question.objects.create(
            mission=self.mission,
            text="Test question?",
            order=1,
            explanation="Test explanation"
        )
        
        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text="Correct answer",
            is_correct=True,
            explanation="This is correct because..."
        )
        
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text="Wrong answer",
            is_correct=False,
            explanation="This is wrong because..."
        )

    def test_mission_creation(self):
        """Test mission creation and string representation"""
        self.assertEqual(str(self.mission), "Mission 1: Test Mission")
        self.assertEqual(self.mission.questions.count(), 1)

    def test_player_profile_creation(self):
        """Test player profile is created automatically"""
        self.assertTrue(hasattr(self.user, 'playerprofile'))
        self.assertEqual(self.user.playerprofile.total_score, 0)

    def test_mission_access(self):
        """Test mission access logic"""
        profile = self.user.playerprofile
        # First mission should be accessible
        self.assertTrue(profile.can_access_mission(self.mission))