from django.test import TestCase
from django.core.management import call_command
from django.db.utils import IntegrityError
from game.models import Mission, Question, Choice
import json
from pathlib import Path

class FixtureTests(TestCase):
    def setUp(self):
        # Load fixtures
        call_command('loaddata', 'questions.json')

    def test_mission_questions_count(self):
        """Test that each mission has exactly 5 questions"""
        for mission in Mission.objects.all():
            question_count = Question.objects.filter(mission=mission).count()
            self.assertEqual(question_count, 5, 
                           f"Mission {mission.title} has {question_count} questions, expected 5")

    def test_question_choices_count(self):
        """Test that each question has exactly 3 choices"""
        for question in Question.objects.all():
            choice_count = Choice.objects.filter(question=question).count()
            self.assertEqual(choice_count, 3, 
                           f"Question {question.text} has {choice_count} choices, expected 3")

    def test_single_correct_answer(self):
        """Test that each question has exactly one correct answer"""
        for question in Question.objects.all():
            correct_choices = Choice.objects.filter(question=question, is_correct=True)
            self.assertEqual(correct_choices.count(), 1,
                           f"Question {question.text} has {correct_choices.count()} correct answers, expected 1")

    def test_question_order(self):
        """Test that questions are ordered correctly within each mission"""
        for mission in Mission.objects.all():
            questions = Question.objects.filter(mission=mission).order_by('order')
            orders = [q.order for q in questions]
            expected_orders = list(range(1, 6))  # 1 to 5
            self.assertEqual(orders, expected_orders,
                           f"Mission {mission.title} questions are not ordered correctly")

    def test_choice_explanations(self):
        """Test that all choices have explanations"""
        for choice in Choice.objects.all():
            self.assertNotEqual(choice.explanation, "",
                              f"Choice '{choice.text}' is missing an explanation")

    def test_json_file_validity(self):
        """Test that the JSON file is valid"""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "questions.json"
        try:
            with open(fixture_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON in questions.json: {e}")

    def test_mission_content_coverage(self):
        """Test that missions cover their intended topics"""
        mission_topics = {
            1: ["charter", "authorize", "scope"],
            2: ["stakeholder", "communication", "engagement"],
            3: ["risk", "change", "management"]
        }
        
        for mission_id, keywords in mission_topics.items():
            mission = Mission.objects.get(id=mission_id)
            questions_text = " ".join([q.text.lower() for q in Question.objects.filter(mission=mission)])
            
            for keyword in keywords:
                self.assertIn(keyword.lower(), questions_text,
                            f"Mission {mission_id} doesn't cover the topic: {keyword}")

    def test_unique_question_texts(self):
        """Test that all questions have unique text"""
        all_questions = Question.objects.values_list('text', flat=True)
        unique_questions = set(all_questions)
        self.assertEqual(len(all_questions), len(unique_questions),
                        "Found duplicate question texts")

    def test_unique_choice_texts_per_question(self):
        """Test that choices for each question are unique"""
        for question in Question.objects.all():
            choices = Choice.objects.filter(question=question).values_list('text', flat=True)
            unique_choices = set(choices)
            self.assertEqual(len(choices), len(unique_choices),
                           f"Found duplicate choices for question: {question.text}")

    def test_question_field_lengths(self):
        """Test that question texts and explanations are reasonable lengths"""
        for question in Question.objects.all():
            self.assertTrue(10 <= len(question.text) <= 200,
                          f"Question text length ({len(question.text)}) outside acceptable range: {question.text}")
            self.assertTrue(20 <= len(question.explanation) <= 500,
                          f"Question explanation length ({len(question.explanation)}) outside acceptable range")

    def test_choice_field_lengths(self):
        """Test that choice texts and explanations are reasonable lengths"""
        for choice in Choice.objects.all():
            self.assertTrue(5 <= len(choice.text) <= 150,
                          f"Choice text length ({len(choice.text)}) outside acceptable range: {choice.text}")
            self.assertTrue(20 <= len(choice.explanation) <= 300,
                          f"Choice explanation length ({len(choice.explanation)}) outside acceptable range")

    def test_mission_progression(self):
        """Test that questions within missions follow a logical progression"""
        for mission in Mission.objects.all():
            questions = Question.objects.filter(mission=mission).order_by('order')
            prev_question = None
            for question in questions:
                if prev_question:
                    # Check that order is sequential
                    self.assertEqual(question.order, prev_question.order + 1,
                                   f"Questions in mission {mission.id} are not in sequential order")
                prev_question = question

    def test_choice_distribution(self):
        """Test that correct answers are reasonably distributed"""
        for mission in Mission.objects.all():
            questions = Question.objects.filter(mission=mission)
            correct_choice_positions = []
            
            for question in questions:
                choices = Choice.objects.filter(question=question).order_by('id')
                correct_position = [i for i, c in enumerate(choices) if c.is_correct][0]
                correct_choice_positions.append(correct_position)
            
            # Check that correct answers aren't all in the same position
            position_counts = [correct_choice_positions.count(i) for i in range(3)]
            for count in position_counts:
                self.assertLess(count, 4,  # No more than 3 correct answers in same position
                              "Correct answers are too predictably positioned")

    def test_explanation_quality(self):
        """Test that explanations are meaningful and different for correct/incorrect answers"""
        for question in Question.objects.all():
            choices = Choice.objects.filter(question=question)
            
            # Get correct and incorrect choice explanations
            correct_exp = [c.explanation for c in choices if c.is_correct][0]
            incorrect_exps = [c.explanation for c in choices if not c.is_correct]
            
            # Check that correct answer explanation contains "Correct"
            self.assertIn("Correct", correct_exp,
                         f"Correct answer explanation should contain 'Correct': {correct_exp}")
            
            # Check that incorrect answer explanations contain "Incorrect"
            for exp in incorrect_exps:
                self.assertIn("Incorrect", exp,
                            f"Incorrect answer explanation should contain 'Incorrect': {exp}")
            
            # Check that explanations are unique for each choice
            all_exps = [c.explanation for c in choices]
            self.assertEqual(len(all_exps), len(set(all_exps)),
                           f"Duplicate explanations found for question: {question.text}")

    def test_fixture_data_integrity(self):
        """Test overall integrity of fixture data"""
        # Test mission count
        mission_count = Mission.objects.count()
        self.assertEqual(mission_count, 3, "Expected exactly 3 missions")
        
        # Test total question count
        question_count = Question.objects.count()
        self.assertEqual(question_count, 15, "Expected exactly 15 questions (5 per mission)")
        
        # Test total choice count
        choice_count = Choice.objects.count()
        self.assertEqual(choice_count, 45, "Expected exactly 45 choices (3 per question)")
        
        # Test relationships
        for question in Question.objects.all():
            self.assertIsNotNone(question.mission, f"Question {question.id} has no mission")
            choices = Choice.objects.filter(question=question)
            self.assertEqual(choices.count(), 3, f"Question {question.id} doesn't have exactly 3 choices")
