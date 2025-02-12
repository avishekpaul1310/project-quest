from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.core.management import call_command

@override_settings(TEST=True)
class SystemFunctionalityTests(TestCase):
    def setUp(self):
        # Load fixtures
        call_command('loaddata', 'missions.json')
        call_command('loaddata', 'questions.json')
        
        # Create test user
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="test@example.com"
        )
        self.client = Client()
        
        # Create player profile and ensure clean state
        self.profile = PlayerProfile.objects.get(user=self.user)
        self.profile.total_score = 0
        self.profile.completed_missions.clear()
        self.profile.save()
        
        # Login the user
        self.client.login(username=self.username, password=self.password)

    def tearDown(self):
        # Clean up after tests
        PlayerAnswer.objects.all().delete()
        self.profile.completed_missions.clear()
        self.profile.total_score = 0
        self.profile.save()

    def test_complete_game_flow(self):
        """Test the entire game flow from start to finish"""
        
        # 1. Check initial state
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile.current_mission_id, 1)
        self.assertEqual(self.profile.total_score, 0)

        # 2. Test mission 1 flow
        mission1 = Mission.objects.get(id=1)
        questions = Question.objects.filter(mission=mission1).order_by('order')
        
        for question in questions:
            # Get correct choice for this question
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            
            # Submit answer
            response = self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['result'])

        # 3. Verify mission completion
        self.profile.refresh_from_db()
        self.assertIn(mission1, self.profile.completed_missions.all())
        self.assertEqual(self.profile.total_score, 50)  # 10 points per correct answer

    def test_mission_progression(self):
        """Test that missions unlock properly"""
        
        # Initially only mission 1 should be accessible
        response = self.client.get(reverse('game:available_missions'))
        self.assertEqual(response.status_code, 200)
        missions = response.json()['missions']
        self.assertTrue(missions[0]['unlocked'])
        self.assertFalse(missions[1]['unlocked'])
        self.assertFalse(missions[2]['unlocked'])

        # Complete mission 1
        self.complete_mission(1)

        # Now mission 2 should be unlocked
        response = self.client.get(reverse('game:available_missions'))
        missions = response.json()['missions']
        self.assertTrue(missions[0]['unlocked'])
        self.assertTrue(missions[1]['unlocked'])
        self.assertFalse(missions[2]['unlocked'])

    def test_scoring_system(self):
        """Test the scoring system"""
        mission = Mission.objects.get(id=1)
        question = Question.objects.filter(mission=mission).first()
        
        # Reset profile score to ensure clean state
        self.profile.total_score = 0
        self.profile.save()
        
        # Test correct answer
        correct_choice = Choice.objects.get(question=question, is_correct=True)
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question.id,
            'choice_id': correct_choice.id
        })
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, 10)

        # Test answering same question again (should not increase score)
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question.id,
            'choice_id': correct_choice.id
        })
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, 10)  # Score should remain the same

        # Test incorrect answer
        question2 = Question.objects.filter(mission=mission)[1]
        incorrect_choice = Choice.objects.filter(question=question2, is_correct=False).first()
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question2.id,
            'choice_id': incorrect_choice.id
        })
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, 10)  # Score shouldn't change

    def complete_mission(self, mission_id):
        """Helper method to complete a mission"""
        mission = Mission.objects.get(id=mission_id)
        questions = Question.objects.filter(mission=mission).order_by('order')
        
        for question in questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            response = self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
            self.assertEqual(response.status_code, 200)