from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
import logging

logger = logging.getLogger(__name__)

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all test methods"""
        logger.debug("Setting up test data...")

    def setUp(self):
        """Set up data for each test method"""
        # Create test missions first
        self.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='• Project charter defines project\n• Authorizes project formally',
            best_practices='• Align with business goals\n• Identify stakeholders early',
            is_active=True
        )
        logger.debug(f"Created mission1: {self.mission1}")
        
        self.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='• Identify stakeholders\n• Analyze their interests',
            best_practices='• Regular communication\n• Address concerns early',
            is_active=True
        )
        logger.debug(f"Created mission2: {self.mission2}")

        # Create test user after missions exist
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        logger.debug(f"Created user: {self.user.username}")
        
        # Create test questions for mission 1
        self.question1 = Question.objects.create(
            mission=self.mission1,
            text='What is a project charter?',
            order=1,
            explanation='A project charter formally authorizes the project.'
        )
        
        # Create choices for question 1
        self.choice1_correct = Choice.objects.create(
            question=self.question1,
            text='A document that formally authorizes the project',
            is_correct=True
        )
        self.choice1_wrong = Choice.objects.create(
            question=self.question1,
            text='A project schedule',
            is_correct=False
        )

    def test_player_profile_creation(self):
        """Test that PlayerProfile is created automatically for new users"""
        self.assertTrue(hasattr(self.user, 'playerprofile'))
        profile = self.user.playerprofile
        logger.debug(f"Profile for user {self.user.username}: {profile}")
        logger.debug(f"Profile's current mission: {profile.current_mission}")
        logger.debug(f"Expected mission: {self.mission1}")
        
        self.assertEqual(profile.total_score, 0)
        self.assertEqual(profile.current_mission, self.mission1)

    def test_mission_access(self):
        """Test mission access logic"""
        profile = self.user.playerprofile
        
        # User should be able to access Mission 1
        self.assertTrue(profile.can_access_mission(self.mission1))
        
        # User should not be able to access Mission 2 yet
        self.assertFalse(profile.can_access_mission(self.mission2))
        
        # After completing Mission 1, user should be able to access Mission 2
        profile.completed_missions.add(self.mission1)
        self.assertTrue(profile.can_access_mission(self.mission2))

    def test_mission_ordering(self):
        """Test that missions are returned in correct order"""
        missions = Mission.objects.all()
        self.assertEqual(missions[0], self.mission1)
        self.assertEqual(missions[1], self.mission2)

    def test_question_uniqueness(self):
        """Test that questions must have unique order within a mission"""
        with self.assertRaises(Exception):
            Question.objects.create(
                mission=self.mission1,
                text='Duplicate order question',
                order=1,  # This should fail as order=1 already exists
                explanation='This should not be created'
            )

class PlayerProgressTests(TestCase):
    def setUp(self):
        # Create mission first
        self.mission = Mission.objects.create(
            title='Test Mission',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        # Create test user after mission exists
        self.user = User.objects.create_user(
            username='testplayer',
            password='testpass123'
        )
        
        self.question = Question.objects.create(
            mission=self.mission,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        
        self.correct_choice = Choice.objects.create(
            question=self.question,
            text='Correct answer',
            is_correct=True
        )
        
        self.wrong_choice = Choice.objects.create(
            question=self.question,
            text='Wrong answer',
            is_correct=False
        )

    def test_answer_recording(self):
        """Test that player answers are recorded correctly"""
        profile = self.user.playerprofile
        
        # Record a correct answer
        answer = PlayerAnswer.objects.create(
            player=profile,
            question=self.question,
            selected_choice=self.correct_choice,
            is_correct=True
        )
        
        # Check that the answer was recorded
        self.assertTrue(
            PlayerAnswer.objects.filter(
                player=profile,
                question=self.question,
                is_correct=True
            ).exists()
        )
        
        # Try to record another answer for the same question (should raise an error)
        with self.assertRaises(Exception):
            PlayerAnswer.objects.create(
                player=profile,
                question=self.question,
                selected_choice=self.wrong_choice,
                is_correct=False
            )

    def test_mission_completion(self):
        """Test mission completion logic"""
        profile = self.user.playerprofile
        
        # Initially, mission should not be completed
        self.assertFalse(profile.completed_missions.filter(id=self.mission.id).exists())
        
        # Add mission to completed missions
        profile.completed_missions.add(self.mission)
        
        # Check that mission is now marked as completed
        self.assertTrue(profile.completed_missions.filter(id=self.mission.id).exists())

class ViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test missions
        self.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        self.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='Test concepts 2',
            best_practices='Test practices 2',
            is_active=True
        )

    def test_login_required(self):
        """Test that views require login"""
        # Try accessing dashboard without login
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view(self):
        """Test dashboard view content"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('game:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')
        self.assertContains(response, 'Project Charter Basics')
        self.assertContains(response, 'Stakeholder Management')

    def test_mission_detail_view(self):
        """Test mission detail view"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test accessing first mission (should be allowed)
        response = self.client.get(reverse('game:mission_detail', args=[self.mission1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/mission_detail.html')
        
        # Test accessing second mission (should be redirected)
        response = self.client.get(reverse('game:mission_detail', args=[self.mission2.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

    def test_submit_answer(self):
        """Test answer submission functionality"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a question and choices
        question = Question.objects.create(
            mission=self.mission1,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        correct_choice = Choice.objects.create(
            question=question,
            text='Correct answer',
            is_correct=True
        )
        wrong_choice = Choice.objects.create(
            question=question,
            text='Wrong answer',
            is_correct=False
        )
        
        # Test submitting correct answer
        response = self.client.post(
            reverse('game:submit_answer', args=[self.mission1.id]),
            {f'question_{question.id}': correct_choice.id}
        )
        
        # Verify redirect after submission
        self.assertEqual(response.status_code, 302)
        
        # Check if score was updated
        self.user.playerprofile.refresh_from_db()
        self.assertEqual(self.user.playerprofile.total_score, 10)
        
        # Check if answer was recorded
        self.assertTrue(
            PlayerAnswer.objects.filter(
                player=self.user.playerprofile,
                question=question,
                is_correct=True
            ).exists()
        )
        
        # Test submitting wrong answer
        response = self.client.post(
            reverse('game:submit_answer', args=[self.mission1.id]),
            {f'question_{question.id}': wrong_choice.id}
        )
        
        # Check if wrong answer was recorded correctly
        self.assertTrue(
            PlayerAnswer.objects.filter(
                player=self.user.playerprofile,
                question=question,
                is_correct=False
            ).exists()
        )        