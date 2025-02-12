from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test mission
        cls.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )

    def setUp(self):
        # Refresh the objects from the database for each test
        self.user.refresh_from_db()
        self.mission.refresh_from_db()