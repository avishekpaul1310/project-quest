from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.core.management import call_command
from django.test.utils import override_settings

@override_settings(TEST=True)
class MissionCompletionTests(TestCase):
    def setUp(self):
        # Load test data
        call_command('loaddata', 'initial_data.json')
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")
        
        # Get player profile
        self.profile = PlayerProfile.objects.get(user=self.user)
        self.profile.total_score = 0
        self.profile.completed_missions.clear()
        self.profile.save()
        
        # Get mission and questions
        self.mission = Mission.objects.get(id=1)
        self.questions = Question.objects.filter(mission=self.mission).order_by('order')

    def test_answer_submission_creates_player_answer(self):
        """Test that submitting an answer creates a PlayerAnswer record"""
        question = self.questions.first()
        correct_choice = Choice.objects.get(question=question, is_correct=True)
        
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question.id,
            'choice_id': correct_choice.id
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PlayerAnswer.objects.filter(
            player=self.profile,
            question=question,
            selected_choice=correct_choice
        ).exists())

    def test_correct_answer_increases_score(self):
        """Test that a correct answer increases the player's score"""
        question = self.questions.first()
        correct_choice = Choice.objects.get(question=question, is_correct=True)
        
        initial_score = self.profile.total_score
        
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question.id,
            'choice_id': correct_choice.id
        })
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, initial_score + 10)

    def test_incorrect_answer_doesnt_increase_score(self):
        """Test that an incorrect answer doesn't increase the score"""
        question = self.questions.first()
        incorrect_choice = Choice.objects.filter(question=question, is_correct=False).first()
        
        initial_score = self.profile.total_score
        
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question.id,
            'choice_id': incorrect_choice.id
        })
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, initial_score)

    def test_mission_completion_tracking(self):
        """Test mission completion tracking logic"""
        # Print initial state
        print(f"\nInitial mission state:")
        print(f"Total questions in mission: {self.questions.count()}")
        print(f"Mission in completed missions: {self.mission in self.profile.completed_missions.all()}")
        
        # Answer all questions correctly
        for question in self.questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            
            # Print pre-submission state
            print(f"\nBefore answering question {question.order}:")
            print(f"Correct answers so far: {PlayerAnswer.objects.filter(player=self.profile, question__mission=self.mission, selected_choice__is_correct=True).count()}")
            
            response = self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
            
            # Print post-submission state
            print(f"After answering question {question.order}:")
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.json()}")
            print(f"Mission in completed missions: {self.mission in self.profile.completed_missions.all()}")
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()['result'])

        # Verify final state
        self.profile.refresh_from_db()
        print(f"\nFinal state:")
        print(f"Total score: {self.profile.total_score}")
        print(f"Correct answers: {PlayerAnswer.objects.filter(player=self.profile, question__mission=self.mission, selected_choice__is_correct=True).count()}")
        print(f"Mission in completed missions: {self.mission in self.profile.completed_missions.all()}")
        
        self.assertIn(self.mission, self.profile.completed_missions.all())
        self.assertEqual(self.profile.total_score, 50)

    def test_partial_completion_state(self):
        """Test that mission isn't marked complete with only some correct answers"""
        # Answer only first 3 questions correctly
        for question in self.questions[:3]:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
        
        self.profile.refresh_from_db()
        self.assertNotIn(self.mission, self.profile.completed_missions.all())
        self.assertEqual(self.profile.total_score, 30)

    def test_question_order_independence(self):
        """Test that questions can be answered in any order"""
        # Answer questions in reverse order
        for question in reversed(list(self.questions)):
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
        
        self.profile.refresh_from_db()
        self.assertIn(self.mission, self.profile.completed_missions.all())
        self.assertEqual(self.profile.total_score, 50)