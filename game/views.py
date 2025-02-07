from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mission, Question, Choice, PlayerAnswer
from django.http import JsonResponse

@login_required
def dashboard(request):
    """Display available missions and user progress."""
    player_profile = request.user.playerprofile
    missions = Mission.objects.filter(is_active=True).order_by('order')
    
    context = {
        'player_profile': player_profile,
        'missions': missions,
    }
    return render(request, 'game/dashboard.html', context)

@login_required
def mission_detail(request, mission_id):
    """Display mission details and questions."""
    mission = get_object_or_404(Mission, pk=mission_id)
    player_profile = request.user.playerprofile
    
    # Check if user can access this mission
    if not player_profile.can_access_mission(mission):
        messages.error(request, 'You need to complete previous missions first!')
        return redirect('game:dashboard')
    
    # Get questions for this mission
    questions = mission.questions.all().order_by('order')
    
    context = {
        'mission': mission,
        'questions': questions,
        'player_profile': player_profile,
    }
    return render(request, 'game/mission_detail.html', context)

@login_required
def submit_answer(request, mission_id):
    """Handle mission question submissions."""
    if request.method != 'POST':
        return redirect('game:mission_detail', mission_id=mission_id)
        
    mission = get_object_or_404(Mission, pk=mission_id)
    player_profile = request.user.playerprofile
    
    # Verify user can access this mission
    if not player_profile.can_access_mission(mission):
        messages.error(request, 'You need to complete previous missions first!')
        return redirect('game:dashboard')
    
    # Process answers
    questions = mission.question_set.all()
    score = 0
    total_questions = questions.count()
    
    for question in questions:
        choice_id = request.POST.get(f'question_{question.id}')
        if not choice_id:
            messages.error(request, 'Please answer all questions!')
            return redirect('game:mission_detail', mission_id=mission_id)
            
        choice = get_object_or_404(Choice, id=choice_id)
        
        # Record the answer
        PlayerAnswer.objects.create(
            player=player_profile,
            question=question,
            selected_choice=choice,
            is_correct=choice.is_correct
        )
        
        if choice.is_correct:
            score += 10  # 10 points per correct answer
    
    # Update player's score
    player_profile.total_score += score
    
    # If all questions are answered correctly, mark mission as completed
    if score == total_questions * 10:
        player_profile.completed_missions.add(mission)
        messages.success(request, f'Congratulations! You completed the mission with a perfect score!')
    else:
        messages.info(request, f'You scored {score} points out of {total_questions * 10}. Try again to get a perfect score!')
    
    player_profile.save()
    
    return redirect('game:dashboard')