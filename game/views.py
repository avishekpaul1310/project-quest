from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerAnswer, PlayerProfile
from django.db import transaction
from django.http import JsonResponse

@login_required
def dashboard(request):
    """Display the user's dashboard with current progress"""
    profile = request.user.playerprofile
    return JsonResponse({
        'current_mission': profile.current_mission_id,
        'total_score': profile.total_score,
        'completed_missions': list(profile.completed_missions.values_list('id', flat=True))
    })

@login_required
def available_missions(request):
    profile = request.user.playerprofile
    missions = Mission.objects.all().order_by('id')
    return JsonResponse({
        'missions': [{
            'id': mission.id,
            'title': mission.title,
            'unlocked': profile.can_access_mission(mission)
        } for mission in missions]
    })

@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    player_profile = request.user.playerprofile
    
    if not player_profile.can_access_mission(mission):
        messages.error(request, 'Complete previous missions first!')
        return redirect('game:dashboard')
    
    questions = mission.questions.all().order_by('order')
    
    return render(request, 'game/mission_detail.html', {
        'mission': mission,
        'questions': questions,
        'player_profile': player_profile,
    })

@login_required
def submit_answer(request):
    """Handle submission of answers to questions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    question_id = request.POST.get('question_id')
    choice_id = request.POST.get('choice_id')

    if not question_id or not choice_id:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        question = get_object_or_404(Question, id=question_id)
        choice = get_object_or_404(Choice, id=choice_id, question=question)
        profile = request.user.playerprofile

        # Check if mission is accessible
        if not profile.can_access_mission(question.mission):
            return JsonResponse({'error': 'Mission not unlocked'}, status=403)

        # Check if question was already answered
        existing_answer = PlayerAnswer.objects.filter(
            player=profile,
            question=question
        ).first()

        if existing_answer:
            return JsonResponse({
                'error': 'Question already answered',
                'result': existing_answer.selected_choice.is_correct,
                'explanation': existing_answer.selected_choice.explanation
            })

        # Record answer
        player_answer = PlayerAnswer.objects.create(
            player=profile,
            question=question,
            selected_choice=choice
        )

        # Update score if answer is correct
        if choice.is_correct:
            profile.total_score = profile.total_score + 10
            profile.save(update_fields=['total_score'])

            # Check if mission is completed
            mission_questions = Question.objects.filter(mission=question.mission)
            answered_correctly = PlayerAnswer.objects.filter(
                player=profile,
                question__mission=question.mission,
                selected_choice__is_correct=True
            ).count()

            if answered_correctly == mission_questions.count():
                profile.completed_missions.add(question.mission)

        return JsonResponse({
            'result': choice.is_correct,
            'explanation': choice.explanation,
            'mission_completed': question.mission in profile.completed_missions.all(),
            'current_score': profile.total_score
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@login_required
def player_progress(request):  # Changed from progress to player_progress
    """Get the player's current progress"""
    profile = request.user.playerprofile
    answered_questions = PlayerAnswer.objects.filter(player=profile)
    
    return JsonResponse({
        'completed_missions': profile.completed_missions.count(),
        'total_score': profile.total_score,
        'questions_answered': answered_questions.count(),
        'current_mission': profile.current_mission_id
    })

@login_required
def take_quiz(request, mission_id):
    """View for taking a mission quiz"""
    mission = get_object_or_404(Mission, pk=mission_id)
    player = request.user.playerprofile

    # Check if user can access this mission
    if not player.can_access_mission(mission):
        messages.error(request, 'Please complete previous missions first.')
        return redirect('game:dashboard')

    # Get questions for this mission
    questions = mission.questions.all().order_by('order')

    if request.method == 'POST':
        with transaction.atomic():
            total_questions = questions.count()
            answers_correct = True
            
            # Delete previous answers for this mission
            PlayerAnswer.objects.filter(
                player=player,
                question__mission=mission
            ).delete()
            
            # Process each question's answer
            for question in questions:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    try:
                        choice = Choice.objects.get(id=choice_id)
                        # Create new answer - score update happens in PlayerAnswer.save()
                        answer = PlayerAnswer.objects.create(
                            player=player,
                            question=question,
                            selected_choice=choice
                        )
                        if not choice.is_correct:
                            answers_correct = False
                    except Choice.DoesNotExist:
                        answers_correct = False
                else:
                    answers_correct = False

            # Refresh player to get updated score
            player.refresh_from_db()
            
            if answers_correct:
                player.completed_missions.add(mission)
                messages.success(request, f'Congratulations! You completed the mission with {player.total_score} points!')
            else:
                messages.info(request, f'You scored {player.total_score} points. Try again to complete the mission!')

            return redirect('game:mission_results', mission_id=mission_id)
        
            answers = PlayerAnswer.objects.filter(
                player=player,
                question__mission=mission
            ).select_related('question', 'selected_choice')
            
            return render(request, 'game/quiz_results.html', {
                'mission': mission,
                'answers': answers,
                'score': player.total_score,
                'mission_completed': answers_correct,
                'next_mission': Mission.objects.filter(order=mission.order + 1).first()
            })

    return render(request, 'game/take_quiz.html', {
        'mission': mission,
        'questions': questions,

    })

@login_required
def mission_results(request, mission_id):
    """View for showing quiz results"""
    mission = get_object_or_404(Mission, pk=mission_id)
    player = request.user.playerprofile
    
    # Get player's answers for this mission
    answers = PlayerAnswer.objects.filter(
        player=player,
        question__mission=mission
    ).select_related('question', 'selected_choice')

    return render(request, 'game/mission_results.html', {
        'mission': mission,
        'answers': answers,
    })

@login_required
def user_stats(request):
    """Get detailed statistics about the user's performance"""
    profile = request.user.playerprofile
    answers = PlayerAnswer.objects.filter(player=profile)
    correct_answers = answers.filter(selected_choice__is_correct=True).count()
    total_attempts = answers.count()
    
    return JsonResponse({
        'missions_completed': profile.completed_missions.count(),
        'correct_answers': correct_answers,
        'total_questions_attempted': total_attempts,
        'accuracy': round(correct_answers / total_attempts * 100 if total_attempts > 0 else 0)
    })