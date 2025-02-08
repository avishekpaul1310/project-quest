from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class MissionProgressTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = PlayerProfile.objects.get(user=self.user)
        
        # Create test missions
        self.missions = []
        for i in range(1, 4):
            mission = Mission.objects.create(
                title=f"Mission {i}",
                order=i,
                key_concepts=f"Concepts {i}",
                best_practices=f"Practices {i}"
            )
            self.missions.append(mission)
            
            # Create 5 questions for each mission
            for j in range(1, 6):
                question = Question.objects.create(
                    mission=mission,
                    text=f"Question {j} for Mission {i}",
                    order=j,
                    explanation=f"Explanation {j}"
                )
                # Create choices
                Choice.objects.create(
                    question=question,
                    text="Correct Answer",
                    is_correct=True,
                    explanation="Correct explanation"
                )
                Choice.objects.create(
                    question=question,
                    text="Wrong Answer",
                    is_correct=False,
                    explanation="Wrong explanation"
                )

    def test_mission_access_sequence(self):
        """Test that missions must be completed in sequence"""
        # First mission should be accessible
        self.assertTrue(self.profile.can_access_mission(self.missions[0]))
        
        # Second and third missions should not be accessible yet
        self.assertFalse(self.profile.can_access_mission(self.missions[1]))
        self.assertFalse(self.profile.can_access_mission(self.missions[2]))
        
        # Complete first mission
        self.profile.completed_missions.add(self.missions[0])
        
        # Now second mission should be accessible, but not third
        self.assertTrue(self.profile.can_access_mission(self.missions[1]))
        self.assertFalse(self.profile.can_access_mission(self.missions[2]))

    def test_mission_scoring(self):
        """Test scoring system for mission completion"""
        mission = self.missions[0]
        questions = mission.questions.all()
        
        # Answer all questions correctly
        for question in questions:
            correct_choice = question.choices.get(is_correct=True)
            PlayerAnswer.objects.create(
                player=self.profile,
                question=question,
                selected_choice=correct_choice
            )
            
        # Check total score (5 correct answers * 10 points each)
        self.assertEqual(self.profile.total_score, 50)
        
        # Change one answer to incorrect
        first_question = questions[0]
        wrong_choice = first_question.choices.get(is_correct=False)
        PlayerAnswer.objects.filter(
            player=self.profile,
            question=first_question
        ).update(selected_choice=wrong_choice)
        
        # Check updated score (4 correct answers * 10 points each)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_score, 40)

    def test_mission_completion_status(self):
        """Test mission completion status tracking"""
        mission = self.missions[0]
        questions = mission.questions.all()
        
        # Answer 4 out of 5 questions correctly
        for question in questions[:4]:
            correct_choice = question.choices.get(is_correct=True)
            PlayerAnswer.objects.create(
                player=self.profile,
                question=question,
                selected_choice=correct_choice
            )
            
        # Mission should not be marked as complete yet
        self.assertFalse(self.profile.completed_missions.filter(id=mission.id).exists())
        
        # Answer last question correctly
        last_question = questions[4]
        correct_choice = last_question.choices.get(is_correct=True)
        PlayerAnswer.objects.create(
            player=self.profile,
            question=last_question,
            selected_choice=correct_choice
        )
        
        # Now mission should be marked as complete
        self.assertTrue(self.profile.completed_missions.filter(id=mission.id).exists())