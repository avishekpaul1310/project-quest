from django.test import TestCase, Client
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile
from django.urls import reverse

class GameTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        
        # Create mission first without validation
        self.mission = Mission.objects.create(
            title='Test Mission',
            description='Test Description',
            order=1
        )
        
        # Create questions
        self.questions = []
        for i in range(5):
            question = Question.objects.create(
                mission=self.mission,
                text=f'Question {i+1}',
                order=i+1
            )
            self.questions.append(question)
            
            # Create choices
            Choice.objects.create(
                question=question,
                text='Correct Answer',
                is_correct=True,
                explanation=f'Explanation for correct answer {i+1}'
            )
            Choice.objects.create(
                question=question,
                text='Wrong Answer 1',
                is_correct=False,
                explanation=f'Explanation for wrong answer 1-{i+1}'
            )
            Choice.objects.create(
                question=question,
                text='Wrong Answer 2',
                is_correct=False,
                explanation=f'Explanation for wrong answer 2-{i+1}'
            )

    def complete_mission(self, mission=None):
        """Helper method to complete a mission"""
        if mission is None:
            mission = self.mission
            
        for question in mission.questions.all():
            correct_choice = question.choices.get(is_correct=True)
            response = self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })
            self.assertEqual(response.status_code, 200)