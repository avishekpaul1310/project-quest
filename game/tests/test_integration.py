from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Mission, Question, Choice, PlayerProfile

class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
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
        
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text="Correct answer",
            is_correct=True,
            explanation="Correct explanation"
        )

    def test_complete_mission(self):
        """Test completing a mission"""
        self.client.login(username='testuser', password='testpass123')
        
        # Access mission
        response = self.client.get(
            reverse('game:mission_detail', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Submit answer
        response = self.client.post(
            reverse('game:take_quiz', args=[self.mission.id]),
            {f'question_{self.question.id}': self.correct_choice.id}
        )
        
        # Check if mission was completed
        profile = self.user.playerprofile
        profile.refresh_from_db()
        self.assertIn(self.mission, profile.completed_missions.all())