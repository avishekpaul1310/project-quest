from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.core.management import call_command
from django.test.utils import override_settings

@override_settings(TEST=True)
class GameFlowTests(TestCase):
    def setUp(self):
        # Load test data
        call_command('loaddata', 'initial_data.json')
        
        # Create test user
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="test@example.com"
        )
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        
        # Get player profile
        self.profile = PlayerProfile.objects.get(user=self.user)
        self.profile.total_score = 0
        self.profile.completed_missions.clear()
        self.profile.save()

        # Get first mission
        self.mission1 = Mission.objects.get(order=1)
        
    def test_part1_initial_state(self):
        """Test the initial state of a new user"""
        print("\nTesting Initial State:")
        
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        print(f"Current mission ID: {self.profile.current_mission_id}")
        print(f"Initial score: {self.profile.total_score}")
        print(f"Completed missions: {list(self.profile.completed_missions.all())}")
        
        self.assertEqual(self.profile.current_mission_id, 1)
        self.assertEqual(self.profile.total_score, 0)
        self.assertEqual(self.profile.completed_missions.count(), 0)

    def test_part2_mission_access(self):
        """Test mission accessibility"""
        print("\nTesting Mission Access:")
        
        # Should be able to access first mission
        response = self.client.get(reverse('game:mission_detail', kwargs={'mission_id': 1}))
        self.assertEqual(response.status_code, 200)
        print(f"Access to Mission 1: {response.status_code == 200}")
        
        # Shouldn't be able to access second mission yet
        response = self.client.get(reverse('game:mission_detail', kwargs={'mission_id': 2}))
        print(f"Response for Mission 2: {response.status_code}")
        self.assertIn(response.status_code, [302, 404])  # Either redirect or not found is acceptable
        print(f"Blocked access to Mission 2: {response.status_code in [302, 404]}")

    def test_part3_answer_questions(self):
        """Test answering questions in first mission"""
        print("\nTesting Question Answers:")
        
        questions = Question.objects.filter(mission=self.mission1).order_by('order')
        
        for i, question in enumerate(questions, 1):
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            
            print(f"\nAnswering Question {i}:")
            print(f"Question ID: {question.id}")
            print(f"Correct Choice ID: {correct_choice.id}")
            
            response = self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            print(f"Response: {data}")
            print(f"Current Score: {self.profile.total_score}")

    def test_part4_mission_completion(self):
        """Test mission completion state after answering all questions"""
        print("\nTesting Mission Completion:")
        
        # Answer all questions correctly first
        questions = Question.objects.filter(mission=self.mission1).order_by('order')
        for question in questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
        
        # Refresh profile from database
        self.profile.refresh_from_db()
        
        print(f"Final Score: {self.profile.total_score}")
        print(f"Mission in completed_missions: {self.mission1 in self.profile.completed_missions.all()}")
        print(f"Completed missions count: {self.profile.completed_missions.count()}")
        
        self.assertEqual(self.profile.total_score, 50)
        self.assertIn(self.mission1, self.profile.completed_missions.all())

    def test_part5_next_mission_unlock(self):
        """Test that next mission unlocks after completing first mission"""
        print("\nTesting Next Mission Unlock:")
        
        # Make sure Mission 2 exists
        mission2 = Mission.objects.get_or_create(
            id=2,
            defaults={
                'title': 'Project Planning Basics',
                'order': 2,
                'key_concepts': '• Project planning fundamentals',
                'best_practices': '• Define clear milestones'
            }
        )[0]
        
        # Complete first mission
        questions = Question.objects.filter(mission=self.mission1).order_by('order')
        for question in questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
        
        # Try accessing second mission
        response = self.client.get(reverse('game:mission_detail', kwargs={'mission_id': 2}))
        print(f"Access to Mission 2 after completion: {response.status_code == 200}")
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)