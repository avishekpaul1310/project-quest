from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

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
        self.assertContains(response, "Test Mission")

    def test_mission_detail_view(self):
        """Test mission detail view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('game:mission_detail', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/mission_detail.html')
        self.assertContains(response, "Test concepts")

    def test_quiz_submission(self):
        """Test quiz submission"""
        self.client.login(username='testuser', password='testpass123')
        
        # Submit quiz answer
        response = self.client.post(
            reverse('game:take_quiz', args=[self.mission.id]),
            {f'question_{self.question.id}': self.correct_choice.id}
        )
        
        # Should redirect to results page
        self.assertEqual(response.status_code, 302)
        
        # Check if score was updated
        profile = self.user.playerprofile
        profile.refresh_from_db()
        self.assertEqual(profile.total_score, 10)