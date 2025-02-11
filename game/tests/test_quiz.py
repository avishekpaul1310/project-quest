from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class QuizSetupTests(TestCase):
    """Tests for quiz setup and configuration"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Create test mission
        self.mission = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        # Create test question
        self.question = Question.objects.create(
            mission=self.mission,
            text='What is a project charter?',
            order=1,
            explanation='A project charter is a formal document...'
        )
        
        # Create choices
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='A formal document that authorizes the project',
            is_correct=True
        )
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text='A project schedule',
            is_correct=False
        )

    def test_question_creation(self):
        """Test that questions are created with correct attributes"""
        self.assertEqual(self.question.mission, self.mission)
        self.assertEqual(self.question.order, 1)
        self.assertEqual(self.question.choices.count(), 2)

    def test_choice_correct_flag(self):
        """Test that only one choice can be marked as correct"""
        # First choice is already correct
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            choice2 = Choice.objects.create(
                question=self.question,
                text="Another correct answer",
                is_correct=True,
                explanation="This should raise an error"
            )

class QuizFunctionalTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Create test mission
        self.mission = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        # Create multiple questions
        self.questions = []
        self.correct_choices = []
        self.wrong_choices = []
        
        for i in range(5):  # Create 5 questions
            question = Question.objects.create(
                mission=self.mission,
                text=f'Test Question {i+1}',
                order=i+1,
                explanation=f'Explanation for question {i+1}'
            )
            self.questions.append(question)
            
            # Create choices for each question
            correct = Choice.objects.create(
                question=question,
                text=f'Correct Answer {i+1}',
                is_correct=True
            )
            wrong = Choice.objects.create(
                question=question,
                text=f'Wrong Answer {i+1}',
                is_correct=False
            )
            
            self.correct_choices.append(correct)
            self.wrong_choices.append(wrong)

    def test_quiz_submission_perfect_score(self):
        """Test quiz submission with all correct answers"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create submission data with all correct answers
        data = {
            f'question_{q.id}': self.correct_choices[i].id
            for i, q in enumerate(self.questions)
        }
        
        with transaction.atomic():
            response = self.client.post(
                reverse('game:take_quiz', args=[self.mission.id]),
                data=data
            )
            
            # Refresh player from database
            player = User.objects.get(username='testuser').playerprofile
            expected_score = len(self.questions) * 10
            
            # Verify score
            self.assertEqual(player.total_score, expected_score)
            
            # Verify mission completion
            self.assertTrue(self.mission in player.completed_missions.all())

    def test_quiz_submission_partial_score(self):
        """Test quiz submission with mixed correct/incorrect answers"""
        self.client.login(username='testuser', password='testpass123')
        
        # Submit mixture of correct and incorrect answers
        data = {
            f'question_{self.questions[0].id}': self.correct_choices[0].id,  # correct
            f'question_{self.questions[1].id}': self.wrong_choices[1].id,    # wrong
            f'question_{self.questions[2].id}': self.correct_choices[2].id,  # correct
            f'question_{self.questions[3].id}': self.wrong_choices[3].id,    # wrong
            f'question_{self.questions[4].id}': self.correct_choices[4].id,  # correct
        }
        
        with transaction.atomic():
            response = self.client.post(
                reverse('game:take_quiz', args=[self.mission.id]),
                data=data
            )
            
            # Refresh player from database
            player = User.objects.get(username='testuser').playerprofile
            
            # Verify score (3 correct answers * 10 points)
            self.assertEqual(player.total_score, 30)
            
            # Verify mission not completed (not all answers correct)
            self.assertFalse(self.mission in player.completed_missions.all())