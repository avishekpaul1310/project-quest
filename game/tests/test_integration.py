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
        self.mission = Mission.objects.create(
            title="Test Mission",
            order=1,
            key_concepts="Test concepts",
            best_practices="Test practices"
        )
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

    def test_complete_mission_flow(self):
        """Test the complete flow of completing a mission"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. Visit dashboard
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Visit mission detail
        response = self.client.get(
            reverse('game:mission_detail', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # 3. Take quiz
        response = self.client.get(
            reverse('game:take_quiz', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Submit quiz with correct answer
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.mission.id]),
            {f'question_{self.question.id}': self.correct_choice.id}
        )
        self.assertEqual(response.status_code, 302)
        
        # 5. Check results
        response = self.client.get(
            reverse('game:quiz_results', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # 6. Verify mission completion
        user_profile = self.user.playerprofile
        self.assertIn(self.mission, user_profile.completed_missions.all())
        self.assertGreater(user_profile.total_score, 0)

    def test_mission_progression(self):
        """Test that missions must be completed in order"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create second mission
        mission2 = Mission.objects.create(
            title="Mission 2",
            order=2,
            key_concepts="Concepts 2",
            best_practices="Practices 2"
        )
        
        # Try to access second mission before completing first
        response = self.client.get(
            reverse('game:mission_detail', args=[mission2.id])
        )
        self.assertEqual(response.status_code, 302)  # Should redirect