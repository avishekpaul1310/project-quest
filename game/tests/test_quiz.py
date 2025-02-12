from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile

class QuizSetupTests(TestCase):
    def setUp(self):
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )
        self.question = Question.objects.create(
            mission=self.mission,
            text='Test Question',
            order=1
        )

    def test_question_creation(self):
        self.assertEqual(self.question.text, 'Test Question')
        self.assertEqual(self.question.order, 1)
        self.assertEqual(self.question.mission, self.mission)

    def test_choice_correct_flag(self):
        correct = Choice.objects.create(
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
        self.assertEqual(Choice.objects.filter(question=self.question, is_correct=True).count(), 1)

class QuizFunctionalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )
        self.question = Question.objects.create(
            mission=self.mission,
            text='Test Question',
            order=1
        )
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct Answer',
            is_correct=True,
            explanation='This is correct'
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
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'correct': True,
            'explanation': 'This is correct',
            'score': 10
        })

    def test_quiz_submission_partial_score(self):
        wrong_choice = Choice.objects.create(
            question=self.question,
            text='Wrong Answer',
            is_correct=False,
            explanation='This is incorrect'
        )
        response = self.client.post(
            reverse('game:submit_answer'),
            {
                'question': self.question.id,
                'choice': wrong_choice.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'correct': False,
            'explanation': 'This is incorrect',
            'score': 0
        })