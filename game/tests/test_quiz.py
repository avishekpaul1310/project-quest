from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class QuizSetupTests(TestCase):
    """Tests for quiz setup and configuration"""
    
    def setUp(self):
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
            explanation="This is why this answer is correct"  # Added explanation
        )
        
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text="Wrong answer",
            is_correct=False,
            explanation="This is why this answer is wrong"  # Added explanation
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
            text="Test question",
            order=1,
            explanation="Question explanation"
        )
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text="Correct answer",
            is_correct=True,
            explanation="Correct choice explanation"  # Added explanation
        )
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text="Wrong answer",
            is_correct=False,
            explanation="Wrong choice explanation"  # Added explanation
        )
    
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