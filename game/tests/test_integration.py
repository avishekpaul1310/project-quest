from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.core.exceptions import ValidationError

class GameIntegrationTests(TestCase):
    """Integration tests for game flow and component interaction"""
    
    def setUp(self):
        # Create test user and client
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.player_profile = self.user.playerprofile
        
        # Create a sequence of missions
        self.missions = []
        for i in range(3):
            mission = Mission.objects.create(
                title=f"Mission {i+1}",
                description=f"Test mission {i+1}",
                order=i+1
            )
            self.missions.append(mission)
            
            # Create questions for each mission
            self.create_mission_questions(mission)

    def create_mission_questions(self, mission):
        """Helper method to create questions for a mission"""
        for i in range(5):
            question = Question.objects.create(
                mission=mission,
                text=f"Question {i+1} for {mission.title}",
                order=i+1,
                explanation=f"Explanation for question {i+1}"
            )
            # Create correct and incorrect choices
            Choice.objects.create(
                question=question,
                text="Correct Answer",
                is_correct=True,
                explanation="This is the correct answer"
            )
            Choice.objects.create(
                question=question,
                text="Wrong Answer",
                is_correct=False,
                explanation="This is the wrong answer"
            )

    def test_user_registration_to_first_mission(self):
        """Test flow from user registration to accessing first mission"""
        # Register new user
        response = self.client.post(reverse('game:register'), {  # Changed from 'register' to 'game:register'
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        
        # Verify PlayerProfile creation
        new_user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(new_user, 'playerprofile'))
        
        # Check first mission accessibility
        self.client.login(username='newuser', password='testpass123')
        response = self.client.get(reverse('game:mission_detail', args=[self.missions[0].id]))
        self.assertEqual(response.status_code, 200)

    def test_mission_progression_flow(self):
        """Test complete flow of mission progression"""
        self.client.login(username='testuser', password='testpass123')
        
        for mission in self.missions:
            # Verify mission access
            response = self.client.get(reverse('game:mission_detail', args=[mission.id]))
            
            if mission.order == 1:
                self.assertEqual(response.status_code, 200)
            else:
                # Should be forbidden until previous mission is complete
                self.assertEqual(response.status_code, 403)
                
                # Complete previous mission
                self._complete_mission(self.missions[mission.order - 2])
                
                # Now should have access
                response = self.client.get(reverse('game:mission_detail', args=[mission.id]))
                self.assertEqual(response.status_code, 200)
            
            # Complete current mission
            self._complete_mission(mission)

    def test_quiz_submission_and_progress_update(self):
        """Test quiz submission flow and progress tracking"""
        self.client.login(username='testuser', password='testpass123')
        mission = self.missions[0]
        
        # Get initial score
        initial_score = self.player_profile.total_score
        
        # Submit quiz with all correct answers
        data = {
            f'question_{q.id}': q.choices.get(is_correct=True).id
            for q in mission.questions.all()
        }
        
        response = self.client.post(
            reverse('game:submit_quiz', args=[mission.id]),
            data=data,
            follow=True
        )
        
        # Verify response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/quiz_results.html')
        
        # Refresh profile and verify updates
        self.player_profile.refresh_from_db()
        self.assertGreater(self.player_profile.total_score, initial_score)
        self.assertTrue(mission in self.player_profile.completed_missions.all())

    def test_game_state_consistency(self):
        """Test consistency of game state across different actions"""
        self.client.login(username='testuser', password='testpass123')
        
        # Complete first mission
        self._complete_mission(self.missions[0])
        
        # Verify game state
        self.player_profile.refresh_from_db()
        self.assertEqual(self.player_profile.completed_missions.count(), 1)
        
        # Try to complete third mission (should fail)
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.missions[2].id]),
            data={},
            follow=True
        )
        self.assertEqual(response.status_code, 403)
        
        # Verify game state remained consistent
        self.player_profile.refresh_from_db()
        self.assertEqual(self.player_profile.completed_missions.count(), 1)

    def test_concurrent_mission_attempts(self):
        """Test handling of concurrent mission attempts"""
        self.client.login(username='testuser', password='testpass123')
        
        # Complete first mission
        self._complete_mission(self.missions[0])
        
        # Try to submit third mission before second (should fail)
        data = {
            f'question_{q.id}': q.choices.get(is_correct=True).id
            for q in self.missions[2].questions.all()
        }
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.missions[2].id]),
            data=data
        )
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Submit second mission (should succeed)
        data = {
            f'question_{q.id}': q.choices.get(is_correct=True).id
            for q in self.missions[1].questions.all()
        }
        response = self.client.post(
            reverse('game:submit_quiz', args=[self.missions[1].id]),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
    
    def _complete_mission(self, mission):
        """Helper method to complete a mission"""
        for question in mission.questions.all():
            correct_choice = question.choices.get(is_correct=True)
            PlayerAnswer.objects.create(
                player=self.player_profile,
                question=question,
                selected_choice=correct_choice
            )
        self.player_profile.completed_missions.add(mission)
        self.player_profile.save()