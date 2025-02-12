from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class GameTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create missions
        cls.missions = []
        cls.questions = []
        cls.choices = []
        
        for i in range(3):
            mission = Mission.objects.create(
                title=f'Test Mission {i+1}',
                description=f'Description {i+1}',
                order=i+1,
                key_concepts='Test concepts',
                best_practices='Test practices'
            )
            cls.missions.append(mission)
            
            # Create exactly 5 questions per mission
            for j in range(5):
                question = Question.objects.create(
                    mission=mission,
                    text=f'Question {j+1} for Mission {i+1}',
                    order=j+1,
                    explanation=f'Explanation {j+1}'
                )
                cls.questions.append(question)
                
                # Create exactly 3 choices per question
                Choice.objects.create(
                    question=question,
                    text='Correct Answer',
                    is_correct=True,
                    explanation='This is correct'
                )
                for k in range(2):
                    Choice.objects.create(
                        question=question,
                        text=f'Wrong Answer {k+1}',
                        is_correct=False,
                        explanation=f'This is incorrect option {k+1}'
                    )
    
    def setUp(self):
        self.client.login(username='testuser', password='testpass123')
        self.profile = PlayerProfile.objects.get(user=self.user)

    def tearDown(self):
        if hasattr(self, 'profile'):
            self.profile.completed_missions.clear()
            self.profile.total_score = 0
            self.profile.current_mission_id = 1
            self.profile.save()

    def complete_mission(self, mission):
        """Helper method to complete a mission"""
        for question in mission.questions.all():
            correct_choice = question.choices.filter(is_correct=True).first()
            PlayerAnswer.objects.create(
                player=self.profile,
                question=question,
                selected_choice=correct_choice
            )
        self.profile.complete_mission(mission)