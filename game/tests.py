from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerProfile, PlayerAnswer
import logging

logger = logging.getLogger(__name__)

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified data for all class methods"""
        # Create test missions first
        cls.mission1 = Mission.objects.create(
            title='Project Charter Basics',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        cls.mission2 = Mission.objects.create(
            title='Stakeholder Management',
            order=2,
            key_concepts='Test concepts 2',
            best_practices='Test practices 2',
            is_active=True
        )

    def setUp(self):
        """Set up data for each test method"""
        # Create a new user for each test
        self.user = User.objects.create_user(
            username=f'testuser_{self._testMethodName}',  # Make username unique for each test
            password='testpass123'
        )
        # Profile is created automatically via signal
        self.profile = PlayerProfile.objects.get(user=self.user)

    def test_mission_access(self):
        """Test mission access logic"""
        # User should be able to access Mission 1
        self.assertTrue(self.profile.can_access_mission(self.mission1))
        
        # User should not be able to access Mission 2 yet
        self.assertFalse(self.profile.can_access_mission(self.mission2))
        
        # After completing Mission 1, user should be able to access Mission 2
        self.profile.completed_missions.add(self.mission1)
        self.assertTrue(self.profile.can_access_mission(self.mission2))

    def test_mission_creation(self):
        """Test mission creation and attributes"""
        self.assertEqual(self.mission1.title, 'Project Charter Basics')
        self.assertEqual(self.mission1.order, 1)
        self.assertTrue(self.mission1.is_active)

    def test_mission_ordering(self):
        """Test that missions are returned in correct order"""
        missions = Mission.objects.filter(is_active=True).order_by('order')
        self.assertEqual(missions[0], self.mission1)
        self.assertEqual(missions[1], self.mission2)

    def test_player_profile_creation(self):
        """Test that PlayerProfile is created automatically for new users"""
        self.assertTrue(hasattr(self.user, 'playerprofile'))
        self.assertEqual(self.profile.total_score, 0)
        self.assertEqual(self.profile.current_mission, self.mission1)

    def test_question_uniqueness(self):
        """Test that questions must have unique order within a mission"""
        Question.objects.create(
            mission=self.mission1,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        
        # Try to create another question with the same order in the same mission
        with self.assertRaises(Exception):
            Question.objects.create(
                mission=self.mission1,
                text='Another question',
                order=1,
                explanation='This should fail'
            )

class PlayerProgressTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test mission
        self.mission = Mission.objects.create(
            title='Test Mission',
            order=1,
            key_concepts='Test concepts',
            best_practices='Test practices',
            is_active=True
        )
        
        # Create test user with unique name
        self.user = User.objects.create_user(
            username=f'testplayer_{self._testMethodName}',
            password='testpass123'
        )
        
        # Get the automatically created profile
        self.profile = PlayerProfile.objects.get(user=self.user)
        
        # Create test question
        self.question = Question.objects.create(
            mission=self.mission,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        
        # Create choices
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
        # First attempt with correct answer
        answer, _ = PlayerAnswer.objects.update_or_create(
            player=self.profile,
            question=self.question,
            defaults={'selected_choice': self.correct_choice}
        )
        self.assertTrue(answer.is_correct)
        
        # Change to wrong answer
        answer.selected_choice = self.wrong_choice
        answer.save()
        self.assertFalse(answer.is_correct)
        
        # Verify only one answer exists
        answer_count = PlayerAnswer.objects.filter(
            player=self.profile,
            question=self.question
        ).count()
        self.assertEqual(answer_count, 1)

    def test_mission_completion(self):
        """Test mission completion logic"""
        # Initially mission should not be completed
        self.assertFalse(self.profile.completed_missions.filter(id=self.mission.id).exists())
        
        # Complete mission
        self.profile.completed_missions.add(self.mission)
        self.assertTrue(self.profile.completed_missions.filter(id=self.mission.id).exists())

class ViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
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
        
        # Create test user
        self.user = User.objects.create_user(
            username=f'testuser_{self._testMethodName}',
            password='testpass123'
        )
        
        # Create test client
        self.client = Client()

    def test_login_required(self):
        """Test that views require login"""
        # Try accessing dashboard without login
        response = self.client.get(reverse('game:dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Try accessing mission detail without login
        response = self.client.get(reverse('game:mission_detail', args=[self.mission1.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_dashboard_view(self):
        """Test dashboard view content"""
        self.client.login(username=self.user.username, password='testpass123')
        response = self.client.get(reverse('game:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')
        self.assertContains(response, 'Project Charter Basics')
        self.assertContains(response, 'Stakeholder Management')

    def test_mission_detail_view(self):
        """Test mission detail view"""
        self.client.login(username=self.user.username, password='testpass123')
        
        # Create a question for testing
        question = Question.objects.create(
            mission=self.mission1,
            text='Test question',
            order=1,
            explanation='Test explanation'
        )
        
        response = self.client.get(reverse('game:mission_detail', args=[self.mission1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/mission_detail.html')
        self.assertContains(response, 'Test question')

    def test_submit_answer(self):
        """Test answer submission functionality"""
        self.client.login(username=self.user.username, password='testpass123')
        
        # Create question and choices
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
        
        # Submit correct answer
        response = self.client.post(
            reverse('game:submit_answer', args=[self.mission1.id]),
            {f'question_{question.id}': correct_choice.id}
        )
        
        self.assertEqual(response.status_code, 302)  # Should redirect to dashboard            