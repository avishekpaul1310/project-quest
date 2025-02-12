from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from game.models import Mission, Question, Choice, PlayerProfile

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
                order=i+1
            )
            # Create choices for each question
            correct_choice = Choice.objects.create(
                question=question,
                text=f"Correct Answer {i+1}",
                is_correct=True
            )
            Choice.objects.create(
                question=question,
                text=f"Wrong Answer {i+1}",
                is_correct=False
            )
            self.questions.append(question)

    def complete_mission(self):
        """Helper method to complete a mission"""
        for question in self.questions:
            correct_choice = Choice.objects.get(question=question, is_correct=True)
            self.client.post(reverse('game:submit_answer'), {
                'question_id': question.id,
                'choice_id': correct_choice.id
            })

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
        # Check if description is present
        self.assertContains(response, self.mission.description)

    def test_take_quiz_view(self):
        response = self.client.get(
            reverse('game:take_quiz', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/take_quiz.html')
        self.assertIn('questions', response.context)
        # Verify questions are present
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
        
        response = self.client.get(
            reverse('game:quiz_results', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/quiz_results.html')
        self.assertIn('score', response.context)
        # Verify the score is correct (10 points per question)
        self.assertEqual(response.context['score'], len(self.questions) * 10)