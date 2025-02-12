from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser_model',
            password='testpass123',
            email='test_model@example.com'
        )
        
        # Create test mission
        cls.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )

    def setUp(self):
        # Get fresh copies of the objects for each test
        self.user.refresh_from_db()
        self.mission.refresh_from_db()
        self.profile = PlayerProfile.objects.get(user=self.user)

    def test_mission_creation(self):
        self.assertEqual(self.mission.title, 'Test Mission')
        self.assertEqual(self.mission.order, 1)
        self.assertEqual(str(self.mission), 'Test Mission')

    def test_player_profile_creation(self):
        self.assertEqual(self.profile.total_score, 0)
        self.assertEqual(self.profile.current_mission_id, 1)
        self.assertEqual(str(self.profile), f'Profile of {self.user.username}')

    def test_mission_access(self):
        self.assertTrue(self.profile.can_access_mission(self.mission))

    def test_question_validation(self):
        question = Question.objects.create(
            mission=self.mission,
            text='Test Question',
            order=1,
            explanation='Test Explanation'
        )
        self.assertEqual(str(question), 'Test Question')
        self.assertEqual(question.mission, self.mission)