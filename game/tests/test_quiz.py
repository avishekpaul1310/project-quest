from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class QuizSetupTests(TestCase):
    """Tests for quiz setup and configuration"""
    
    def setUp(self):
        self.mission = Mission.objects.create(
            title="Test Mission",
            description="Test mission description",
            order=1,
            completion_points=10
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
            explanation="This is why this answer is correct"
        )
        
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text="Wrong answer",
            is_correct=False,
            explanation="This is why this answer is wrong"
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

@override_settings(TEST=True)            
class QuizFunctionalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.player_profile = PlayerProfile.objects.create(
            user=self.user,
            total_score=0
        )
        
        self.mission = Mission.objects.create(
            title="Test Mission",
            description="Test mission description",
            order=1,
            completion_points=10
        )
        
        # Create multiple questions for the mission
        self.questions = []
        self.correct_choices = []
        self.wrong_choices = []
        
        for i in range(5):
            question = Question.objects.create(
                mission=self.mission,
                text=f"Test question {i+1}",
                order=i+1,
                explanation=f"Question {i+1} explanation"
            )
            self.questions.append(question)
            
            correct = Choice.objects.create(
                question=question,
                text=f"Correct answer {i+1}",
                is_correct=True,
                explanation=f"Correct choice explanation {i+1}"
            )
            self.correct_choices.append(correct)
            
            wrong = Choice.objects.create(
                question=question,
                text=f"Wrong answer {i+1}",
                is_correct=False,
                explanation=f"Wrong choice explanation {i+1}"
            )
            self.wrong_choices.append(wrong)

    def test_quiz_submission_perfect_score(self):
        """Test quiz submission with all correct answers"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create submission data with all correct answers
        data = {
            f'question_{q.id}': self.correct_choices[i].id
            for i, q in enumerate(self.questions)
        }
        
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.mission.id]),
            data=data
        )
        
        # Refresh player from database
        self.player_profile.refresh_from_db()
        expected_score = len(self.questions) * self.mission.completion_points
        
        # Verify score
        self.assertEqual(self.player_profile.total_score, expected_score)
        
        # Verify mission completion
        self.assertTrue(self.mission in self.player_profile.completed_missions.all())

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
        
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.mission.id]),
            data=data
        )
        
        # Refresh player from database
        self.player_profile.refresh_from_db()
        
        # Verify score (3 correct answers * mission completion points)
        expected_score = 3 * self.mission.completion_points
        self.assertEqual(self.player_profile.total_score, expected_score)
        
        # Verify mission not completed (not all answers correct)
        self.assertFalse(self.mission in self.player_profile.completed_missions.all())