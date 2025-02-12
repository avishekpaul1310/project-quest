from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class MissionCompletionTests(TestCase):
    def setUp(self):
        # Create test user and get their profile
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.player_profile = self.user.playerprofile
        
        # Create a sequence of missions
        self.missions = []
        for i in range(3):  # Create 3 missions
            mission = Mission.objects.create(
                title=f"Mission {i+1}",
                description=f"Test mission {i+1}",
                order=i+1
            )
            self.missions.append(mission)
            
            # Create 5 questions for each mission
            for j in range(5):
                question = Question.objects.create(
                    mission=mission,
                    text=f"Question {j+1} for Mission {i+1}",
                    order=j+1,
                    explanation=f"Explanation for question {j+1}"
                )
                
                # Create one correct and one wrong choice
                Choice.objects.create(
                    question=question,
                    text="Correct Answer",
                    is_correct=True,
                    explanation="This is correct"
                )
                Choice.objects.create(
                    question=question,
                    text="Wrong Answer",
                    is_correct=False,
                    explanation="This is wrong"
                )

    def test_mission_access_rules(self):
        """Test that missions are properly locked/unlocked based on completion"""
        self.client.login(username='testuser', password='testpass123')
        
        # First mission should be accessible
        response = self.client.get(reverse('game:mission_detail', args=[self.missions[0].id]))
        self.assertEqual(response.status_code, 200)
        
        # Second mission should be locked
        response = self.client.get(reverse('game:mission_detail', args=[self.missions[1].id]))
        self.assertEqual(response.status_code, 403)
        
        # Complete first mission
        self._complete_mission(self.missions[0])
        
        # Now second mission should be accessible
        response = self.client.get(reverse('game:mission_detail', args=[self.missions[1].id]))
        self.assertEqual(response.status_code, 200)

    def test_mission_completion_sequence(self):
        """Test that missions must be completed in order"""
        self.client.login(username='testuser', password='testpass123')
        
        # Try to complete second mission without completing first
        response = self._attempt_mission(self.missions[1])
        self.assertEqual(response.status_code, 403)
        
        # Complete first mission
        self._complete_mission(self.missions[0])
        
        # Now completing second mission should work
        response = self._attempt_mission(self.missions[1])
        self.assertEqual(response.status_code, 200)

    def test_mission_progress_tracking(self):
        """Test that mission progress is tracked correctly"""
        self.client.login(username='testuser', password='testpass123')
        
        # Initially no missions completed
        self.assertEqual(self.player_profile.completed_missions.count(), 0)
        
        # Complete first mission
        self._complete_mission(self.missions[0])
        self.assertEqual(self.player_profile.completed_missions.count(), 1)
        
        # Verify progress data structure
        progress = self.player_profile.get_mission_progress(self.missions[0])
        self.assertEqual(progress['total_questions'], 5)
        self.assertEqual(progress['correct_answers'], 5)
        self.assertTrue(progress['is_completed'])

    def test_mission_completion_requirements(self):
        """Test that all questions must be answered correctly to complete a mission"""
        self.client.login(username='testuser', password='testpass123')
        
        mission = self.missions[0]
        questions = mission.questions.all()
        
        # Answer 4 out of 5 questions correctly
        for question in questions[:4]:
            correct_choice = question.choices.get(is_correct=True)
            PlayerAnswer.objects.create(
                player=self.player_profile,
                question=question,
                selected_choice=correct_choice
            )
        
        # Answer last question incorrectly
        wrong_choice = questions[4].choices.get(is_correct=False)
        PlayerAnswer.objects.create(
            player=self.player_profile,
            question=questions[4],
            selected_choice=wrong_choice
        )
        
        # Mission should not be completed
        self.assertFalse(self.player_profile.has_completed_mission(mission))
        self.assertFalse(mission in self.player_profile.completed_missions.all())

    def _complete_mission(self, mission):
        """Helper method to complete a mission by answering all questions correctly"""
        for question in mission.questions.all():
            correct_choice = question.choices.get(is_correct=True)
            PlayerAnswer.objects.create(
                player=self.player_profile,
                question=question,
                selected_choice=correct_choice
            )
        self.player_profile.complete_mission(mission)

    def _attempt_mission(self, mission):
        """Helper method to attempt completing a mission through the view"""
        data = {}
        for question in mission.questions.all():
            correct_choice = question.choices.get(is_correct=True)
            data[f'question_{question.id}'] = correct_choice.id
        
        return self.client.post(
            reverse('game:submit_quiz', args=[mission.id]),
            data=data
        )