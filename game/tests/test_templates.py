from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Mission, Question, Choice

class TemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mission = Mission.objects.create(
            title="Test Mission",
            order=1,
            key_concepts="Test concepts",
            best_practices="Test practices"
        )

    def test_base_template(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('game:dashboard'))
        
        # Check navigation elements
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'My Progress')
        self.assertContains(response, 'Logout')
        self.assertContains(response, self.user.username)

    def test_dashboard_template(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('game:dashboard'))
        
        self.assertContains(response, 'Project Management Missions')
        self.assertContains(response, self.mission.title)

    def test_mission_detail_template(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('game:mission_detail', args=[self.mission.id])
        )
        
        self.assertContains(response, self.mission.title)
        self.assertContains(response, 'Key Concepts')
        self.assertContains(response, 'Best Practices')