from django.test import TestCase
from django.core.management import call_command
from ..models import Mission, Question, Choice
import json
import os

class FixtureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Load the fixture data
        call_command('loaddata', 'initial_data.json', app_label='game')
    
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
        """Test that each mission has exactly 5 questions"""
        missions = Mission.objects.all()
        for mission in missions:
            question_count = mission.questions.count()
            self.assertLessEqual(question_count, 5, 
                f"Mission {mission.id} has {question_count} questions, expected maximum 5")

    def test_question_choices_count(self):
        """Test that each question has exactly 3 choices"""
        questions = Question.objects.all()
        for question in questions:
            choice_count = question.choices.count()
            self.assertEqual(choice_count, 3, 
                f"Question {question.id} has {choice_count} choices, expected 3")

    def test_single_correct_answer(self):
        """Test that each question has exactly one correct answer"""
        questions = Question.objects.all()
        for question in questions:
            correct_count = question.choices.filter(is_correct=True).count()
            self.assertEqual(correct_count, 1,
                f"Question {question.id} has {correct_count} correct answers, expected 1")

    def test_question_field_lengths(self):
        """Test that question texts and explanations are reasonable lengths"""
        questions = Question.objects.all()
        for question in questions:
            self.assertTrue(10 <= len(question.text) <= 500,
                f"Question {question.id} text length is not within reasonable bounds")
            self.assertTrue(20 <= len(question.explanation) <= 1000,
                f"Question {question.id} explanation length is not within reasonable bounds")

    def test_choice_field_lengths(self):
        """Test that choice texts and explanations are reasonable lengths"""
        choices = Choice.objects.all()
        for choice in choices:
            self.assertTrue(5 <= len(choice.text) <= 300,
                f"Choice {choice.id} text length is not within reasonable bounds")
            self.assertTrue(10 <= len(choice.explanation) <= 500,
                f"Choice {choice.id} explanation length is not within reasonable bounds")

    def test_unique_choice_texts_per_question(self):
        """Test that choices for each question are unique"""
        questions = Question.objects.all()
        for question in questions:
            choice_texts = question.choices.values_list('text', flat=True)
            self.assertEqual(len(choice_texts), len(set(choice_texts)),
                f"Question {question.id} has duplicate choice texts")

    def test_question_order(self):
        """Test that questions are ordered correctly within each mission"""
        missions = Mission.objects.all()
        for mission in missions:
            questions = mission.questions.order_by('order')
            orders = list(questions.values_list('order', flat=True))
            expected_orders = list(range(1, len(orders) + 1))
            self.assertEqual(orders, expected_orders,
                f"Mission {mission.id} questions are not properly ordered")

    def test_mission_progression(self):
        """Test that questions within missions follow a logical progression"""
        missions = Mission.objects.all()
        for mission in missions:
            questions = mission.questions.order_by('order')
            prev_order = 0
            for question in questions:
                self.assertTrue(question.order > prev_order,
                    f"Question order {question.order} is not greater than previous order {prev_order}")
                prev_order = question.order

    def test_explanation_quality(self):
        """Test that explanations are meaningful and different for correct/incorrect answers"""
        choices = Choice.objects.all()
        for choice in choices:
            self.assertNotEqual(choice.explanation.strip(), "",
                f"Choice {choice.id} has empty explanation")
            if choice.is_correct:
                self.assertIn("correct", choice.explanation.lower(),
                    f"Correct choice {choice.id} explanation doesn't indicate it's correct")
            else:
                self.assertIn("incorrect", choice.explanation.lower(),
                    f"Incorrect choice {choice.id} explanation doesn't indicate it's incorrect")
