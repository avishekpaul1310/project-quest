from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class MissionFlowTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.profile = PlayerProfile.objects.get(user=self.user)
        
        # Create missions
        self.missions = []
        for i in range(2):
            mission = Mission.objects.create(
                title=f'Mission {i+1}',
                description=f'Description {i+1}',
                order=i+1
            )
            self.missions.append(mission)
            
            # Create 5 questions per mission
            for j in range(5):
                question = Question.objects.create(
                    mission=mission,
                    text=f'Question {j+1}',
                    order=j+1
                )
                # Add 3 choices per question
                Choice.objects.create(
                    question=question,
                    text='Correct',
                    is_correct=True,
                    explanation='Correct explanation'
                )
                for k in range(2):
                    Choice.objects.create(
                        question=question,
                        text=f'Wrong {k+1}',
                        is_correct=False,
                        explanation=f'Wrong explanation {k+1}'
                    )

    def test_mission_progression(self):
        """Test that missions must be completed in order"""
        # First mission should be accessible
        self.assertTrue(self.profile.can_access_mission(self.missions[0]))
        
        # Second mission should not be accessible yet
        self.assertFalse(self.profile.can_access_mission(self.missions[1]))
        
        # Complete first mission
        for question in self.missions[0].questions.all():
            correct_choice = question.choices.filter(is_correct=True).first()
            PlayerAnswer.objects.create(
                player=self.profile,
                question=question,
                selected_choice=correct_choice
            )
        self.profile.complete_mission(self.missions[0])
        
        # Now second mission should be accessible
        self.assertTrue(self.profile.can_access_mission(self.missions[1]))

    def test_mission_completion(self):
        """Test mission completion logic"""
        mission = self.missions[0]
        
        # Initially mission should not be completed
        self.assertFalse(self.profile.has_completed_mission(mission))
        
        # Complete all questions correctly
        for question in mission.questions.all():
            correct_choice = question.choices.filter(is_correct=True).first()
            PlayerAnswer.objects.create(
                player=self.profile,
                question=question,
                selected_choice=correct_choice
            )
        
        # Complete mission
        self.profile.complete_mission(mission)
        
        # Check mission is now completed
        self.assertTrue(self.profile.has_completed_mission(mission))