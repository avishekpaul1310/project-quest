from django.test import TestCase
from django.urls import reverse, resolve
from .. import views

class URLTests(TestCase):
    def test_dashboard_url(self):
        url = reverse('game:dashboard')
        self.assertEqual(resolve(url).func, views.dashboard)

    def test_mission_detail_url(self):
        url = reverse('game:mission_detail', args=[1])
        self.assertEqual(resolve(url).func, views.mission_detail)

    def test_take_quiz_url(self):
        url = reverse('game:take_quiz', args=[1])
        self.assertEqual(resolve(url).func, views.take_quiz)

    def test_submit_quiz_url(self):
        url = reverse('game:submit_quiz', args=[1])
        self.assertEqual(resolve(url).func, views.submit_quiz)

    def test_quiz_results_url(self):
        url = reverse('game:quiz_results', args=[1])
        self.assertEqual(resolve(url).func, views.quiz_results)