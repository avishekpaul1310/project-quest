from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class ScoreDisplayTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.client.login(username='testuser', password='testpass')
        
        # Create mission with required fields
        self.mission = Mission.objects.create(
            title="Test Mission",
            description="Test Description",
            order=1,
            key_concepts="Test concepts",
            best_practices="Test practices"
        )
        
        # Create questions and choices
        for i in range(5):
            question = Question.objects.create(
                mission=self.mission,
                text=f"Question {i+1}",
                order=i+1,
                explanation=f"Explanation for question {i+1}"
            )
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
                explanation="This is incorrect"
            )

    def test_score_updates_immediately(self):
        # Submit answers and check score update
        question = self.mission.questions.first()
        correct_choice = question.choices.filter(is_correct=True).first()
        
        response = self.client.post(reverse('game:submit_answer'), {
            'question': question.id,
            'choice': correct_choice.id
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"score":', status_code=200)

    def test_score_persists_after_refresh(self):
        # Submit answer and get score
        question = self.mission.questions.first()
        correct_choice = question.choices.filter(is_correct=True).first()
        
        self.client.post(reverse('game:submit_answer'), {
            'question': question.id,
            'choice': correct_choice.id
        })
        
        # Refresh page and check score persists
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.playerprofile.total_score)