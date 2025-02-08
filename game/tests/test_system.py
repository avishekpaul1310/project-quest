from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.core.management import call_command

class SystemFunctionalityTests(TestCase):
    def setUp(self):
        # Load fixtures
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
        
        # Create player profile
        self.profile = PlayerProfile.objects.get(user=self.user)
        
        # Login the user
        self.client.login(username=self.username, password=self.password)

    def test_complete_game_flow(self):
        """Test the entire game flow from start to finish"""
        
        # 1. Check initial state
        response = self.client.get(reverse('dashboard'))
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
            response = self.client.post(reverse('submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn('result', response.json())
            self.assertTrue(response.json()['result'])

        # 3. Verify mission 1 completion
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.completed_missions.filter(id=1).exists())
        self.assertEqual(self.profile.total_score, 50)  # 10 points per correct answer

    def test_mission_progression(self):
        """Test that missions unlock properly"""
        
        # Initially only mission 1 should be accessible
        response = self.client.get(reverse('available_missions'))
        self.assertEqual(response.status_code, 200)
        missions = response.json()['missions']
        self.assertTrue(missions[0]['unlocked'])
        self.assertFalse(missions[1]['unlocked'])
        self.assertFalse(missions[2]['unlocked'])

        # Complete mission 1
        self._complete_mission(1)

        # Now mission 2 should be unlocked
        response = self.client.get(reverse('available_missions'))
        missions = response.json()['missions']
        self.assertTrue(missions[0]['unlocked'])
        self.assertTrue(missions[1]['unlocked'])
        self.assertFalse(missions[2]['unlocked'])

    def test_scoring_system(self):
        """Test the scoring system"""
        mission = Mission.objects.get(id=1)
        questions = Question.objects.filter(mission=mission).order_by('order')
        
        # Test correct answer
        question = questions[0]
        correct_choice = Choice.objects.get(question=question, is_correct=True)
        response = self.client.post(reverse('submit_answer'), {
            'question_id': question.id,
            'choice_id': correct_choice.id
        })
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, 10)

        # Test incorrect answer
        question = questions[1]
        incorrect_choice = Choice.objects.filter(question=question, is_correct=False).first()
        response = self.client.post(reverse('submit_answer'), {
            'question_id': question.id,
            'choice_id': incorrect_choice.id
        })
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, 10)  # Score shouldn't change

    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        
        # Check initial progress
        response = self.client.get(reverse('progress'))
        self.assertEqual(response.status_code, 200)
        progress = response.json()
        self.assertEqual(progress['completed_missions'], 0)
        self.assertEqual(progress['total_score'], 0)
        self.assertEqual(progress['questions_answered'], 0)

        # Complete some questions
        self._answer_questions(1, 3)  # Answer 3 questions from mission 1

        # Check updated progress
        response = self.client.get(reverse('progress'))
        progress = response.json()
        self.assertEqual(progress['questions_answered'], 3)
        self.assertEqual(progress['completed_missions'], 0)  # Mission not complete yet

    def test_error_handling(self):
        """Test system error handling"""
        
        # Test invalid question ID
        response = self.client.post(reverse('submit_answer'), {
            'question_id': 9999,
            'choice_id': 1
        })
        self.assertEqual(response.status_code, 404)

        # Test invalid choice ID
        question = Question.objects.first()
        response = self.client.post(reverse('submit_answer'), {
            'question_id': question.id,
            'choice_id': 9999
        })
        self.assertEqual(response.status_code, 404)

        # Test answering question from locked mission
        self._complete_mission(1)
        question = Question.objects.filter(mission__id=3).first()
        choice = Choice.objects.filter(question=question).first()
        response = self.client.post(reverse('submit_answer'), {
            'question_id': question.id,
            'choice_id': choice.id
        })
        self.assertEqual(response.status_code, 403)

    def test_user_statistics(self):
        """Test user statistics tracking"""
        
        # Complete first mission
        self._complete_mission(1)
        
        response = self.client.get(reverse('user_stats'))
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        
        self.assertEqual(stats['missions_completed'], 1)
        self.assertEqual(stats['correct_answers'], 5)
        self.assertEqual(stats['total_questions_attempted'], 5)
        self.assertEqual(stats['accuracy'], 100)

    def _complete_mission(self, mission_id):
        """Helper method to complete a mission"""
        questions = Question.objects.filter(mission__id=mission_id).order_by('order')
        for question in questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            self.client.post(reverse('submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })

    def _answer_questions(self, mission_id, count):
        """Helper method to answer a specific number of questions"""
        questions = Question.objects.filter(mission__id=mission_id).order_by('order')[:count]
        for question in questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            self.client.post(reverse('submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })