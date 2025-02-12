from django.test import TestCase, Client
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile
from django.urls import reverse

class GameTestBase(TestCase):
    def setUp(self):
        # Create user and login
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        
        # Create mission without validation
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )
        
        # Create 5 questions with choices
        for i in range(5):
            question = Question.objects.create(
                mission=self.mission,
                text=f'Question {i+1}',
                order=i+1,
                explanation=f'Explanation {i+1}'
            )
            
            Choice.objects.create(
                question=question,
                text='Correct Answer',
                is_correct=True,
                explanation=f'Correct explanation {i+1}'
            )
            Choice.objects.create(
                question=question,
                text='Wrong Answer 1',
                is_correct=False,
                explanation=f'Wrong explanation 1-{i+1}'
            )
            Choice.objects.create(
                question=question,
                text='Wrong Answer 2',
                is_correct=False,
                explanation=f'Wrong explanation 2-{i+1}'
            )