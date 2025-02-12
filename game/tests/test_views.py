from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

class ViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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
            order=1
        )
        
        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct Answer',
            is_correct=True,
            explanation='This is correct'
        )
        
        Choice.objects.create(
            question=self.question,
            text='Wrong Answer',
            is_correct=False,
            explanation='This is incorrect'
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')

    def test_mission_detail_view(self):
        response = self.client.get(reverse('game:mission_detail', args=[self.mission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/mission_detail.html')

    def test_quiz_results_view(self):
        response = self.client.get(reverse('game:quiz_results', args=[self.mission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/quiz_results.html')

    def test_submit_quiz_view(self):
        response = self.client.post(
            reverse('game:submit_answer'),
            {
                'question': self.question.id,
                'choice': self.correct_choice.id
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_take_quiz_view(self):
        response = self.client.get(reverse('game:take_quiz', args=[self.mission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/take_quiz.html')