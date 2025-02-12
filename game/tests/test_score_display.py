from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile
from django.core.management import call_command

class ScoreDisplayTests(TestCase):
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
        
        # Get player profile and first mission
        self.profile = PlayerProfile.objects.get(user=self.user)
        self.mission = Mission.objects.get(order=1)

    def test_score_updates_immediately(self):
        """Test that score updates are immediately reflected"""
        print("\nTesting Real-time Score Updates:")
        
        # Get all questions for the first mission
        questions = Question.objects.filter(mission=self.mission).order_by('order')
        
        # Track score through each answer
        current_score = 0
        for i, question in enumerate(questions, 1):
            # Get the correct choice for this question
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            
            # Submit answer
            print(f"\nSubmitting answer {i}:")
            print(f"Previous score: {current_score}")
            
            response = self.client.post(
                reverse('game:submit_answer'),
                {'question_id': question.id, 'choice_id': correct_choice.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simulate AJAX request
            )
            
            # Update expected score
            current_score += 10
            
            # Get actual score from database
            self.profile.refresh_from_db()
            actual_score = self.profile.total_score
            
            print(f"Expected score: {current_score}")
            print(f"Actual score: {actual_score}")
            print(f"Response score: {response.json().get('score')}")
            
            # Verify score in response matches expected score
            self.assertEqual(response.json().get('score'), current_score)
            # Verify database score matches expected score
            self.assertEqual(actual_score, current_score)
            
    def test_score_persists_after_refresh(self):
        """Test that score persists after page refresh"""
        print("\nTesting Score Persistence:")
        
        # Answer first question correctly
        question = Question.objects.filter(mission=self.mission).first()
        correct_choice = Choice.objects.get(question=question, is_correct=True)
        
        # Submit answer and get initial score
        response = self.client.post(
            reverse('game:submit_answer'),
            {'question_id': question.id, 'choice_id': correct_choice.id}
        )
        initial_score = response.json().get('score')
        print(f"Initial score after answer: {initial_score}")
        
        # Simulate page refresh by getting dashboard
        dashboard_response = self.client.get(reverse('game:dashboard'))
        self.profile.refresh_from_db()
        print(f"Score after refresh: {self.profile.total_score}")
        
        # Verify score persists
        self.assertEqual(self.profile.total_score, initial_score)