from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerAnswer, PlayerProfile
from django.db import transaction
from django.http import JsonResponse

@login_required
def dashboard(request):
    player_profile = request.user.playerprofile
    missions = Mission.objects.filter(is_active=True).order_by('order')
    return render(request, 'game/dashboard.html', {
        'player_profile': player_profile,
        'missions': missions,
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
def submit_answer(request, mission_id):
    if request.method != 'POST':
        return redirect('game:mission_detail', mission_id=mission_id)
    
    mission = get_object_or_404(Mission, pk=mission_id)
    player_profile = request.user.playerprofile
    
    if not player_profile.can_access_mission(mission):
        messages.error(request, 'Complete previous missions first!')
        return redirect('game:dashboard')
    
    questions = mission.questions.all()
    score = 0
    total_questions = questions.count()
    
    for question in questions:
        choice_id = request.POST.get(f'question_{question.id}')
        if not choice_id:
            messages.error(request, 'Please answer all questions!')
            return redirect('game:mission_detail', mission_id=mission_id)
            
        choice = get_object_or_404(Choice, id=choice_id)
        
        # Record the answer
        PlayerAnswer.objects.update_or_create(
            player=player_profile,
            question=question,
            defaults={
                'selected_choice': choice,
                'is_correct': choice.is_correct
            }
        )
        
        if choice.is_correct:
            score += 10
    
    # Update player's score
    player_profile.total_score += score
    
    # If perfect score, mark mission as completed
    if score == total_questions * 10:
        player_profile.completed_missions.add(mission)
        messages.success(request, f'Congratulations! Mission completed with perfect score!')
    else:
        messages.info(request, f'You scored {score} points. Try again for a perfect score!')
    
    player_profile.save()
    return redirect('game:dashboard')

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