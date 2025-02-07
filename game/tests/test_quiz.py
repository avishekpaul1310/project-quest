from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from game.models import Mission, Question, Choice, PlayerProfile, PlayerAnswer

class QuizTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Create test mission
        self.mission = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        # Create test questions
        self.question1 = Question.objects.create(
            mission=self.mission,
            text='What is a project charter?',
            order=1,
            explanation='A project charter is a formal document...'
        )
        
        self.question2 = Question.objects.create(
            mission=self.mission,
            text='Who approves the project charter?',
            order=2,
            explanation='The project sponsor approves...'
        )
        
        # Create choices for question 1
        self.q1_correct = Choice.objects.create(
            question=self.question1,
            text='A formal document that authorizes the project',
            is_correct=True
        )
        self.q1_wrong = Choice.objects.create(
            question=self.question1,
            text='A project schedule',
            is_correct=False
        )
        
        # Create choices for question 2
        self.q2_correct = Choice.objects.create(
            question=self.question2,
            text='Project Sponsor',
            is_correct=True
        )
        self.q2_wrong = Choice.objects.create(
            question=self.question2,
            text='Team Member',
            is_correct=False
        )

    def test_question_creation(self):
        """Test that questions are created correctly"""
        self.assertEqual(self.question1.mission, self.mission)
        self.assertEqual(self.question1.order, 1)
        self.assertTrue(len(self.question1.choices.all()) == 2)

    def test_choice_uniqueness(self):
        """Test that only one choice can be correct per question"""
        new_correct = Choice.objects.create(
            question=self.question1,
            text='Another correct answer',
            is_correct=True
        )
        self.q1_correct.refresh_from_db()
        self.assertFalse(self.q1_correct.is_correct)
        self.assertTrue(new_correct.is_correct)

    def test_quiz_access(self):
        """Test quiz access restrictions"""
        self.client.login(username='testuser', password='testpass123')
        
        # Try accessing first mission (should work)
        response = self.client.get(reverse('game:take_quiz', args=[self.mission.id]))
        self.assertEqual(response.status_code, 200)
        
        # Create a second mission
        mission2 = Mission.objects.create(
            title='Advanced Topics',
            order=2,
            key_concepts='Advanced concepts',
            best_practices='Advanced practices',
            is_active=True
        )
        
        # Try accessing second mission (should redirect)
        response = self.client.get(reverse('game:take_quiz', args=[mission2.id]))
        self.assertEqual(response.status_code, 302)

    def test_quiz_submission(self):
        """Test quiz submission and scoring"""
        self.client.login(username='testuser', password='testpass123')
        
        # Submit correct answers
        response = self.client.post(
            reverse('game:take_quiz', args=[self.mission.id]),
            data={
                f'question_{self.question1.id}': self.q1_correct.id,
                f'question_{self.question2.id}': self.q2_correct.id,
            }
        )
        
        # Check if answers were recorded
        player = self.user.playerprofile
        self.assertTrue(self.question1.is_answered_correctly_by(player))
        self.assertTrue(self.question2.is_answered_correctly_by(player))
        
        # Check score (10 points per correct answer)
        self.assertEqual(player.total_score, 20)
        
        # Check if mission was completed
        self.assertTrue(self.mission in player.completed_missions.all())

    def test_quiz_partial_completion(self):
        """Test partial quiz completion"""
        self.client.login(username='testuser', password='testpass123')
        
        # Submit mixed answers (one correct, one wrong)
        response = self.client.post(
            reverse('game:take_quiz', args=[self.mission.id]),
            data={
                f'question_{self.question1.id}': self.q1_correct.id,
                f'question_{self.question2.id}': self.q2_wrong.id,
            }
        )
        
        player = self.user.playerprofile
        self.assertEqual(player.total_score, 10)  # Only one correct answer
        self.assertFalse(self.mission in player.completed_missions.all())

    def test_results_page(self):
        """Test the quiz results page"""
        self.client.login(username='testuser', password='testpass123')
        
        # Submit answers
        self.client.post(
            reverse('game:take_quiz', args=[self.mission.id]),
            data={
                f'question_{self.question1.id}': self.q1_correct.id,
                f'question_{self.question2.id}': self.q2_wrong.id,
            }
        )
        
        # Check results page
        response = self.client.get(reverse('game:mission_results', args=[self.mission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question1.text)
        self.assertContains(response, self.question2.explanation)