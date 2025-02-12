from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
from django.conf import settings

class ViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")
        
        # Create test mission
        self.mission = Mission.objects.create(
            title="Test Mission",
            description="Test mission description",
            order=1
        )

        # Create test questions
        self.questions = []
        for i in range(3):  # Create 3 test questions
            question = Question.objects.create(
                mission=self.mission,
                text=f"Test Question {i+1}",
                order=i+1,
                explanation=f"Explanation for question {i+1}"
            )
            # Create choices for each question
            correct_choice = Choice.objects.create(
                question=question,
                text=f"Correct Answer {i+1}",
                is_correct=True,
                explanation=f"This is why answer {i+1} is correct"
            )
            Choice.objects.create(
                question=question,
                text=f"Wrong Answer {i+1}",
                is_correct=False,
                explanation=f"This is why answer {i+1} is wrong"
            )
            self.questions.append(question)

    def complete_mission(self):
        """Helper method to complete a mission by answering all questions correctly"""
        player_profile = self.user.playerprofile
        
        # Answer all questions correctly
        for question in self.questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            # Create PlayerAnswer for each question
            PlayerAnswer.objects.create(
                player=player_profile,
                question=question,
                selected_choice=correct_choice
            )
        
        # Mark mission as completed
        player_profile.completed_missions.add(self.mission)
        player_profile.save()

        # Add quiz results to session
        session = self.client.session
        session['quiz_results'] = {
            'answers': [answer.id for answer in PlayerAnswer.objects.filter(
                player=player_profile,
                question__mission=self.mission
            )],
            'score': 100,
            'passed': True
        }
        session.save()

    def test_dashboard_view(self):
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')
        self.assertIn('missions', response.context)

    def test_mission_detail_view(self):
        response = self.client.get(
            reverse('game:mission_detail', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/mission_detail.html')
        self.assertIn('mission', response.context)
        self.assertContains(response, self.mission.description)

    def test_take_quiz_view(self):
        response = self.client.get(
            reverse('game:take_quiz', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/take_quiz.html')
        self.assertIn('questions', response.context)
        self.assertTrue(len(response.context['questions']) > 0)

    def test_submit_quiz_view(self):
        question = self.questions[0]
        correct_choice = Choice.objects.get(question=question, is_correct=True)
        response = self.client.post(reverse('game:submit_answer'), {
            'question_id': question.id,
            'choice_id': correct_choice.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['result'])
        self.assertEqual(data['score'], 10)

    def test_quiz_results_view(self):
        # Complete the mission first
        self.complete_mission()
        
        # Get user's profile
        user_profile = self.user.playerprofile
        
        # Add quiz results to session (if not already done in complete_mission)
        if 'quiz_results' not in self.client.session:
            session = self.client.session
            session['quiz_results'] = {
                'answers': [answer.id for answer in PlayerAnswer.objects.filter(
                    player=user_profile,
                    question__mission=self.mission
                )],
                'score': 100,
                'passed': True
            }
            session.save()
        
        # Test quiz results view
        response = self.client.get(
            reverse('game:quiz_results', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/quiz_results.html')
        
        # Check context data
        self.assertIn('score', response.context)
        self.assertIn('passed', response.context)
        self.assertIn('answers', response.context)