from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

class MissionFlowTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
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
        profile = PlayerProfile.objects.get(user=self.user)
        
        # First mission should be accessible
        self.assertTrue(profile.can_access_mission(self.missions[0]))
        
        # Second mission should not be accessible yet
        self.assertFalse(profile.can_access_mission(self.missions[1]))