from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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