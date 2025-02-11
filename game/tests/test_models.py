from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

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
        
        # Create second mission
        mission2 = Mission.objects.create(
            title="Test Mission 2",
            order=2,
            key_concepts="Test concepts 2",
            best_practices="Test practices 2"
        )
        # Second mission should be locked
        self.assertFalse(profile.can_access_mission(mission2))

    def test_answer_scoring(self):
        """Test answer submission and scoring"""
        profile = self.user.playerprofile
        initial_score = profile.total_score
        
        # Submit correct answer
        answer = PlayerAnswer.objects.create(
            player=profile,
            question=self.question,
            selected_choice=self.correct_choice
        )
        
        profile.refresh_from_db()
        self.assertEqual(profile.total_score, initial_score + 10)