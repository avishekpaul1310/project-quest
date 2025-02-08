from django.test import TestCase
from django.core.exceptions import ValidationError
from game.models import Mission, Question, Choice

class MissionRequirementsTests(TestCase):
    def setUp(self):
        self.mission = Mission.objects.create(
            title="Test Mission",
            order=1,
            key_concepts="Test concepts",
            best_practices="Test practices"
        )

    def create_question(self, order):
        """Helper method to create a question with choices"""
        question = Question.objects.create(
            mission=self.mission,
            text=f"Test Question {order}",
            order=order,
            explanation="Test explanation"
        )
        # Create choices for the question
        Choice.objects.create(
            question=question,
            text="Correct Answer",
            is_correct=True,
            explanation="Correct explanation"
        )
        Choice.objects.create(
            question=question,
            text="Wrong Answer",
            is_correct=False,
            explanation="Wrong explanation"
        )
        return question

    def test_mission_requires_five_questions(self):
        """Test that a mission must have exactly 5 questions"""
        # Initially the mission should raise ValidationError as it has no questions
        with self.assertRaises(ValidationError):
            self.mission.clean()

        # Add 3 questions (not enough)
        for i in range(1, 4):
            self.create_question(order=i)
        
        with self.assertRaises(ValidationError):
            self.mission.clean()

        # Add remaining 2 questions (correct amount)
        for i in range(4, 6):
            self.create_question(order=i)
        
        # Should not raise ValidationError with exactly 5 questions
        try:
            self.mission.clean()
        except ValidationError:
            self.fail("Mission with 5 questions raised ValidationError")

        # Add an extra question (too many)
        self.create_question(order=6)
        
        with self.assertRaises(ValidationError):
            self.mission.clean()

    def test_question_order_within_mission(self):
        """Test that questions are ordered correctly within a mission"""
        # Create 5 questions in random order
        orders = [3, 1, 5, 2, 4]
        for order in orders:
            self.create_question(order=order)

        # Get questions in order
        questions = self.mission.questions.all()
        
        # Verify questions are returned in correct order
        self.assertEqual(len(questions), 5)
        for i, question in enumerate(questions, 1):
            self.assertEqual(question.order, i)

    def test_mission_questions_choices(self):
        """Test that each question has at least one correct answer"""
        # Create a question without choices
        question = Question.objects.create(
            mission=self.mission,
            text="Test Question",
            order=1,
            explanation="Test explanation"
        )

        with self.assertRaises(ValidationError):
            question.clean()

        # Add incorrect choice
        Choice.objects.create(
            question=question,
            text="Wrong Answer",
            is_correct=False,
            explanation="Wrong explanation"
        )

        with self.assertRaises(ValidationError):
            question.clean()

        # Add correct choice
        Choice.objects.create(
            question=question,
            text="Correct Answer",
            is_correct=True,
            explanation="Correct explanation"
        )

        # Should not raise ValidationError with at least one correct answer
        try:
            question.clean()
        except ValidationError:
            self.fail("Question with correct answer raised ValidationError")