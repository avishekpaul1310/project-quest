from django.urls import reverse
from .base import GameTestBase

class ViewTests(GameTestBase):
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

    def test_take_quiz_view(self):
        response = self.client.get(
            reverse('game:take_quiz', args=[self.mission.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/take_quiz.html')
        self.assertIn('questions', response.context)

    def test_submit_quiz_view(self):
        question = self.questions[0]
        correct_choice = question.choices.get(is_correct=True)
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