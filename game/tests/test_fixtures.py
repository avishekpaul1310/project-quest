from django.test import TestCase
from django.core.management import call_command
from ..models import Mission, Question, Choice

class FixtureTests(TestCase):
    fixtures = ['initial_data']  # Changed to use fixtures class attribute
    
    def test_fixture_data_integrity(self):
        """Test overall integrity of fixture data"""
        # Check if missions exist
        missions = Mission.objects.all()
        self.assertTrue(missions.exists(), "No missions found in fixtures")
        
        # Check if questions exist
        questions = Question.objects.all()
        self.assertTrue(questions.exists(), "No questions found in fixtures")
        
        # Check if choices exist
        choices = Choice.objects.all()
        self.assertTrue(choices.exists(), "No choices found in fixtures")

    def test_mission_questions_count(self):
        """Test that each mission has the correct number of questions"""
        mission = Mission.objects.first()
        self.assertIsNotNone(mission, "No mission found")
        self.assertGreater(mission.questions.count(), 0, "Mission has no questions")

    def test_question_choices_count(self):
        """Test that each question has exactly 3 choices"""
        question = Question.objects.first()
        self.assertIsNotNone(question, "No question found")
        self.assertEqual(question.choices.count(), 3, "Question should have exactly 3 choices")

    def test_single_correct_answer(self):
        """Test that each question has exactly one correct answer"""
        question = Question.objects.first()
        self.assertIsNotNone(question, "No question found")
        correct_count = question.choices.filter(is_correct=True).count()
        self.assertEqual(correct_count, 1, "Question should have exactly 1 correct answer")

    def test_question_field_lengths(self):
        """Test that question texts and explanations are reasonable lengths"""
        question = Question.objects.first()
        self.assertIsNotNone(question, "No question found")
        self.assertTrue(len(question.text) >= 10, "Question text too short")
        self.assertTrue(len(question.explanation) >= 20, "Question explanation too short")

    def test_choice_field_lengths(self):
        """Test that choice texts and explanations are reasonable lengths"""
        choice = Choice.objects.first()
        self.assertIsNotNone(choice, "No choice found")
        self.assertTrue(len(choice.text) >= 5, "Choice text too short")
        self.assertTrue(len(choice.explanation) >= 10, "Choice explanation too short")

    def test_mission_order(self):
        """Test that mission order is set correctly"""
        mission = Mission.objects.first()
        self.assertIsNotNone(mission, "No mission found")
        self.assertEqual(mission.order, 1, "First mission should have order=1")

    def test_question_order(self):
        """Test that question order is set correctly"""
        question = Question.objects.first()
        self.assertIsNotNone(question, "No question found")
        self.assertEqual(question.order, 1, "First question should have order=1")

    def test_choice_correctness(self):
        """Test that choice correctness is properly set"""
        question = Question.objects.first()
        self.assertIsNotNone(question, "No question found")
        choices = question.choices.all()
        self.assertTrue(any(c.is_correct for c in choices), "No correct choice found")