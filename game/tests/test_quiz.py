from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile

class QuizTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser_quiz',
            password='testpass123',
            email='test_quiz@example.com'
        )
        
        # Login
        self.client.login(username='testuser_quiz', password='testpass123')
        
        # Get profile
        self.profile = PlayerProfile.objects.get(user=self.user)
        
        # Create mission
        self.mission = Mission.objects.create(
            title='Quiz Mission',
            description='Quiz Description',
            order=1
        )
        
        # Create question
        self.question = Question.objects.create(
            mission=self.mission,
            text='Quiz Question',
            order=1,
            explanation='Quiz Explanation'
        )
        
        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct Answer',
            is_correct=True,
            explanation='This is correct'
        )
        
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text='Wrong Answer',
            is_correct=False,
            explanation='This is incorrect'
        )

    def test_question_creation(self):
        self.assertEqual(self.question.text, 'Quiz Question')
        self.assertEqual(self.question.order, 1)
        self.assertEqual(self.question.mission, self.mission)

    def test_choice_correct_flag(self):
        self.assertEqual(
            Choice.objects.filter(question=self.question, is_correct=True).count(),
            1
        )

    def test_quiz_submission_perfect_score(self):
        response = self.client.post(
            reverse('game:submit_answer'),
            {
                'question': self.question.id,
                'choice': self.correct_choice.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'correct': True,
                'explanation': 'This is correct',
                'score': 10
            }
        )

    def test_quiz_submission_wrong_answer(self):
        response = self.client.post(
            reverse('game:submit_answer'),
            {
                'question': self.question.id,
                'choice': self.wrong_choice.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'correct': False,
                'explanation': 'This is incorrect',
                'score': 0
            }
        )