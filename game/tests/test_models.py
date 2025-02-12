from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.core.exceptions import ValidationError
from .base import GameTestBase  # Import GameTestBase from the appropriate module

class ModelTests(GameTestBase):
    def test_mission_creation(self):
        mission = self.mission
        self.assertEqual(str(mission), f"Mission {mission.order}: {mission.title}")
        self.assertEqual(mission.questions.count(), 5)

    def test_player_profile_creation(self):
        self.assertTrue(hasattr(self.user, 'playerprofile'))
        self.assertEqual(self.user.playerprofile.total_score, 0)

    def test_mission_access(self):
        profile = self.user.playerprofile
        self.assertTrue(profile.can_access_mission(self.mission))

    def test_question_validation(self):
        # Test that a mission requires exactly 5 questions
        with self.assertRaises(ValidationError):
            mission = Mission.objects.create(
                title='Invalid Mission',
                description='Test',
                order=2
            )
            mission.clean()