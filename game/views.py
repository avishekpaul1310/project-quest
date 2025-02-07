from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Mission, Question, Choice, PlayerAnswer

@login_required
def dashboard(request):
    player_profile = request.user.playerprofile
    missions = Mission.objects.filter(is_active=True).order_by('order')
    return render(request, 'game/dashboard.html', {
        'player_profile': player_profile,
        'missions': missions,
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
        score = 0
        total_questions = questions.count()
        answers_correct = True  # Track if all answers are correct
        
        # Process each question's answer
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                try:
                    choice = Choice.objects.get(id=choice_id)
                    # Create or update player's answer
                    answer, _ = PlayerAnswer.objects.update_or_create(
                        player=player,
                        question=question,
                        defaults={'selected_choice': choice}
                    )
                    if choice.is_correct:
                        score += 10  # 10 points per correct answer
                    else:
                        answers_correct = False
                except Choice.DoesNotExist:
                    answers_correct = False
            else:
                answers_correct = False

        # Update player's score and completion status
        if score > 0:  # Only update score if points were earned
            player.add_score(score)
            if answers_correct:  # Only complete mission if all answers correct
                player.completed_missions.add(mission)
                messages.success(request, f'Congratulations! You completed the mission with {score} points!')
            else:
                messages.info(request, f'You scored {score} points. Try again to complete the mission!')
        
        return redirect('game:mission_results', mission_id=mission_id)

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