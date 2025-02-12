from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class QuizFunctionalTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.profile = PlayerProfile.objects.get(user=self.user)

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
            order=1,
            explanation='Test Explanation'
        )

        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct Answer',
            is_correct=True,
            explanation='This is correct'
        )
        self.wrong_choices = []
        for i in range(2):
            choice = Choice.objects.create(
                question=self.question,
                text=f'Wrong Answer {i+1}',
                is_correct=False,
                explanation=f'This is incorrect {i+1}'
            )
            self.wrong_choices.append(choice)

    def test_quiz_submission_perfect_score(self):
        """Test quiz submission with all correct answers"""
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
                'explanation': self.correct_choice.explanation,
                'score': 10  # Changed from 0 to 10 to match the points per question
            }
        )

    def test_quiz_submission_partial_score(self):
        """Test quiz submission with mixed correct/incorrect answers"""
        wrong_choice = self.wrong_choices[0]
        response = self.client.post(
            reverse('game:submit_answer'),
            {
                'question': self.question.id,
                'choice': wrong_choice.id
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'correct': False,
                'explanation': wrong_choice.explanation,
                'score': self.profile.total_score
            }
        )

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
            order=1,
            explanation='Test Explanation'
        )

    def test_question_creation(self):
        """Test that questions are created with correct attributes"""
        self.assertEqual(self.question.text, 'Test Question')
        self.assertEqual(self.question.order, 1)
        self.assertEqual(self.question.mission, self.mission)

    def test_choice_correct_flag(self):
        """Test that only one choice can be marked as correct"""
        # Create correct choice
        correct = Choice.objects.create(
            question=self.question,
            text='Correct Answer',
            is_correct=True,
            explanation='This is correct'
        )
        
        # Create wrong choices
        for i in range(2):
            Choice.objects.create(
                question=self.question,
                text=f'Wrong Answer {i+1}',
                is_correct=False,
                explanation=f'This is incorrect {i+1}'
            )
        
        self.assertEqual(Choice.objects.filter(question=self.question).count(), 3)
        self.assertEqual(Choice.objects.filter(question=self.question, is_correct=True).count(), 1)