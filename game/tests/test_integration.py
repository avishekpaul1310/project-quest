from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create multiple missions
        self.missions = []
        for i in range(3):
            mission = Mission.objects.create(
                title=f"Mission {i+1}",
                order=i+1,
                key_concepts=f"Concepts {i+1}",
                best_practices=f"Practices {i+1}"
            )
            self.missions.append(mission)
            
            # Add questions to each mission
            for j in range(5):
                question = Question.objects.create(
                    mission=mission,
                    text=f"Question {j+1} for Mission {i+1}",
                    order=j+1,
                    explanation=f"Explanation {j+1}"
                )
                
                # Add choices
                Choice.objects.create(
                    question=question,
                    text="Correct answer",
                    is_correct=True,
                    explanation="Correct explanation"
                )
                Choice.objects.create(
                    question=question,
                    text="Wrong answer",
                    is_correct=False,
                    explanation="Wrong explanation"
                )

    def test_complete_user_journey(self):
        """Test complete user journey through the game"""
        # 1. Login
        self.client.login(username='testuser', password='testpass123')
        
        # 2. Visit dashboard
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Complete each mission
        for mission in self.missions:
            # Visit mission detail page
            response = self.client.get(
                reverse('game:mission_detail', args=[mission.id])
            )
            self.assertEqual(response.status_code, 200)
            
            # Get questions and submit correct answers
            questions = mission.questions.all()
            answer_data = {}
            for question in questions:
                correct_choice = question.choices.get(is_correct=True)
                answer_data[f'question_{question.id}'] = correct_choice.id
            
            # Submit quiz
            response = self.client.post(
                reverse('game:take_quiz', args=[mission.id]),
                answer_data
            )
            self.assertEqual(response.status_code, 302)  # Should redirect
            
            # Check mission completion
            profile = self.user.playerprofile
            profile.refresh_from_db()
            self.assertIn(mission, profile.completed_missions.all())
        
        # 4. Check final score
        profile = self.user.playerprofile
        expected_score = len(self.missions) * 5 * 10  # 3 missions * 5 questions * 10 points
        self.assertEqual(profile.total_score, expected_score)