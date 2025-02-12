from django.test import TestCase, Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.core.management import call_command

@override_settings(TEST=True)
class SystemFunctionalityTests(TestCase):
    def setUp(self):
        # Create user and profile
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.client.login(username='testuser', password='testpass')
        
        # Create mission
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices'
        )
        
        # Create questions with proper explanations
        for i in range(5):
            question = Question.objects.create(
                mission=self.mission,
                text=f'Question {i+1}',
                order=i+1
            )
            Choice.objects.create(
                question=question,
                text='Correct',
                is_correct=True,
                explanation='This is the correct answer'
            )
            Choice.objects.create(
                question=question,
                text='Incorrect',
                is_correct=False,
                explanation='This is an incorrect answer'
            )

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
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        missions = response.context['missions']
        
        # Test initial state
        self.assertTrue(missions[0]['unlocked'])
        self.assertFalse(missions[1]['unlocked'])
        self.assertFalse(missions[2]['unlocked'])
        
        # Complete first mission
        self.complete_mission()
        
        # Check if second mission is unlocked
        response = self.client.get(reverse('game:dashboard'))
        missions = response.context['missions']
        self.assertTrue(missions[1]['unlocked'])

    def test_scoring_system(self):
        initial_score = self.user.playerprofile.total_score
        self.assertEqual(initial_score, 0)
        
        # Answer first question correctly
        question = self.questions[0]
        correct_choice = question.choices.get(is_correct=True)
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question.id,
            'choice_id': correct_choice.id
        })
        
        data = response.json()
        self.assertTrue(data['result'])
        self.assertEqual(data['score'], 10)

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