from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )

    def test_mission_creation(self):
        self.assertEqual(self.mission.title, 'Test Mission')
        self.assertEqual(self.mission.order, 1)

    def test_player_profile_creation(self):
        profile = PlayerProfile.objects.get(user=self.user)
        self.assertEqual(profile.total_score, 0)
        self.assertEqual(profile.current_mission_id, 1)

    def test_mission_access(self):
        profile = PlayerProfile.objects.get(user=self.user)
        self.assertTrue(profile.can_access_mission(self.mission))

    def test_question_validation(self):
        question = Question.objects.create(
            mission=self.mission,
            text='Test Question',
            order=1
        )
        self.assertEqual(str(question), 'Test Question')
        self.assertEqual(question.mission, self.mission)