from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Mission, Question, Choice, PlayerProfile

@override_settings(TEST=True)
class ViewTests(TestCase):
    def setUp(self):
        # Create test user
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
        
        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text="Correct answer",
            is_correct=True,
            explanation="Correct explanation"
        )
        
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text="Wrong answer",
            is_correct=False,
            explanation="Wrong explanation"
        )

    def test_dashboard_view(self):
        # Test unauthenticated access
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')
        self.assertIn('missions', response.context)

    def test_mission_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Test valid mission access
        response = self.client.get(
            reverse('game:mission_detail', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/mission_detail.html')
        
        # Test invalid mission access
        response = self.client.get(
            reverse('game:mission_detail', args=[999])
        )
        self.assertEqual(response.status_code, 404)

    def test_take_quiz_view(self):
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('game:take_quiz', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/take_quiz.html')
        self.assertIn('questions', response.context)

    def test_submit_quiz_view(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Test submission with correct answer
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.mission.id]),
            {f'question_{self.question.id}': self.correct_choice.id}
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to results
        
        # Test submission with wrong answer
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.mission.id]),
            {f'question_{self.question.id}': self.wrong_choice.id}
        )
        self.assertEqual(response.status_code, 302)

    def test_quiz_results_view(self):
        self.client.login(username='testuser', password='testpass123')
        
        # First submit a quiz
        self.client.post(
            reverse('game:submit_quiz', args=[self.mission.id]),
            {f'question_{self.question.id}': self.correct_choice.id}
        )
        
        # Then check results
        response = self.client.get(
            reverse('game:quiz_results', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/quiz_results.html')