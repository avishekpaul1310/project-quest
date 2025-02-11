from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Mission, Question, Choice, PlayerProfile

class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
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
            explanation="Correct explanation"
        )
        
        Choice.objects.create(
            question=self.question,
            text="Wrong answer 1",
            is_correct=False,
            explanation="Wrong explanation 1"
        )
        
        Choice.objects.create(
            question=self.question,
            text="Wrong answer 2",
            is_correct=False,
            explanation="Wrong explanation 2"
        )

    def test_complete_mission(self):
        """Test completing a mission"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Access mission detail page
        response = self.client.get(
            reverse('game:mission_detail', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Submit correct answer
        response = self.client.post(
            reverse('game:submit_answer', args=[self.mission.id]),
            {f'question_{self.question.id}': self.correct_choice.id}
        )
        
        # Should redirect back to mission detail
        self.assertEqual(response.status_code, 302)
        
        # Check if mission was completed
        profile = self.user.playerprofile
        profile.refresh_from_db()
        self.assertIn(self.mission, profile.completed_missions.all())
        
        # Verify score was updated
        self.assertGreater(profile.total_score, 0)