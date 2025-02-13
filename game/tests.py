from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mission, Question, UserProfile, UserMissionProgress

class GameTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test mission
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )
        
        # Create test question
        self.question = Question.objects.create(
            mission=self.mission,
            text='Test Question',
            option_a='Correct Answer',
            option_b='Wrong Answer 1',
            option_c='Wrong Answer 2',
            option_d='Wrong Answer 3',
            correct_option='A'
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')

    def test_take_quiz(self):
        response = self.client.get(
            reverse('game:take_quiz', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/take_quiz.html')

    def test_quiz_submission(self):
        response = self.client.post(
            reverse('game:take_quiz', args=[self.mission.id]),
            {f'question_{self.question.id}': 'A'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after submission
        
        # Check if progress was recorded
        progress = UserMissionProgress.objects.get(
            user=self.user,
            mission=self.mission
        )
        self.assertTrue(progress.completed)
        self.assertEqual(progress.score, 10)