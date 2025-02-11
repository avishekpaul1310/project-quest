from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Mission, Question, Choice, PlayerProfile

class ViewTests(TestCase):
    def setUp(self):
        # Create test client
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
        
        # Create test question with choices
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

    def test_dashboard_view(self):
        """Test dashboard view"""
        # Try accessing dashboard without login
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')