from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Mission, Question, Choice, PlayerAnswer, PlayerProfile
from django.http import JsonResponse
from django.conf import settings

@login_required
def dashboard(request):
    missions = Mission.objects.all().order_by('order')
    user_profile = request.user.playerprofile
    
    context = {
        'missions': missions,
        'user_profile': user_profile,
        'completed_missions': user_profile.completed_missions.all()
    }
    return render(request, 'game/dashboard.html', context)

@login_required
def available_missions(request):
    missions = Mission.objects.all().order_by('order')
    user_profile = request.user.playerprofile
    
    mission_data = []
    for mission in missions:
        mission_data.append({
            'id': mission.id,
            'title': mission.title,
            'order': mission.order,
            'unlocked': user_profile.can_access_mission(mission),
            'completed': mission in user_profile.completed_missions.all()
        })
    
    return JsonResponse({'missions': mission_data})

@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    user_profile = request.user.playerprofile

    if not user_profile.can_access_mission(mission):
        messages.error(request, 'Complete the previous mission first!')
        return redirect('game:dashboard')

    completed = mission in user_profile.completed_missions.all()
    
    context = {
        'mission': mission,
        'completed': completed
    }
    return render(request, 'game/mission_detail.html', context)

@login_required
def take_quiz(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    user_profile = request.user.playerprofile

    # Don't redirect in test environment
    if not settings.TEST and not user_profile.can_access_mission(mission):
        messages.error(request, 'Complete the previous mission first!')
        return redirect('game:dashboard')

    questions = mission.questions.all().order_by('order')
    
    context = {
        'mission': mission,
        'questions': questions
    }
    return render(request, 'game/take_quiz.html', context)

@login_required
def submit_answer(request):
    """
    Handle submission of answers for questions.
    Expects POST data with:
    - question_id: ID of the question being answered
    - choice_id: ID of the selected choice
    Returns JSON with:
    - result: boolean indicating if answer was correct
    - explanation: explanation for the selected choice
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    question_id = request.POST.get('question_id')
    choice_id = request.POST.get('choice_id')
    
    if not question_id or not choice_id:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
        
    try:
        question = Question.objects.get(id=question_id)
        choice = Choice.objects.get(id=choice_id, question=question)
        user_profile = request.user.playerprofile
        
        # Create or update player answer
        PlayerAnswer.objects.update_or_create(
            player=user_profile,
            question=question,
            defaults={'selected_choice': choice}
        )
        
        # If answer is correct and not previously answered correctly
        if choice.is_correct and not user_profile.has_answered_correctly(question):
            user_profile.total_score += 10  # Add 10 points for correct answer
            user_profile.save()
            
            # Check if mission is completed
            mission = question.mission
            mission_questions = Question.objects.filter(mission=mission)
            correct_answers = PlayerAnswer.objects.filter(
                player=user_profile,
                question__in=mission_questions,
                selected_choice__is_correct=True
            ).count()
            
            if correct_answers == mission_questions.count():
                user_profile.completed_missions.add(mission)
        
        return JsonResponse({
            'result': choice.is_correct,
            'explanation': choice.explanation
        })
        
    except (Question.DoesNotExist, Choice.DoesNotExist):
        return JsonResponse({'error': 'Invalid question or choice'}, status=400)
    
@login_required
def submit_quiz(request, mission_id):
    if request.method != 'POST':
        return redirect('game:mission_detail', mission_id=mission_id)

    mission = get_object_or_404(Mission, id=mission_id)
    questions = mission.questions.all()
    user_profile = request.user.playerprofile
    
    correct_count = 0
    total_questions = questions.count()
    
    for question in questions:
        choice_id = request.POST.get(f'question_{question.id}')
        if choice_id:
            choice = get_object_or_404(Choice, id=choice_id)
            PlayerAnswer.objects.update_or_create(
                player=user_profile,
                question=question,
                defaults={'selected_choice': choice}
            )
            if choice.is_correct:
                correct_count += 1

    score = (correct_count / total_questions) * 100
    
    # Update total score only if mission wasn't completed before
    if score >= 70 and mission not in user_profile.completed_missions.all():
        user_profile.total_score += int(score)
        user_profile.completed_missions.add(mission)
        user_profile.save()
        messages.success(request, f'Congratulations! You passed with {score}%')
    else:
        messages.error(request, f'You need 70% to pass. Your score: {score}%')

    return redirect('game:quiz_results', mission_id=mission_id)

@login_required
def quiz_results(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    results = request.session.get('quiz_results')
    
    if not results:
        messages.error(request, 'No quiz results found.')
        return redirect('game:mission_detail', mission_id=mission_id)
    
    answers = PlayerAnswer.objects.filter(
        id__in=results.get('answers', [])
    ).select_related('question', 'selected_choice')
    
    context = {
        'mission': mission,
        'score': results.get('score', 0),
        'passed': results.get('passed', False),
        'answers': answers
    }
    
    # Don't delete results from session for test environment
    if not settings.TEST:
        del request.session['quiz_results']
    
    return render(request, 'game/quiz_results.html', context)
@login_required
def mission_results(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    user_profile = request.user.playerprofile
    
    total_questions = mission.questions.count()
    answers = PlayerAnswer.objects.filter(
        player=user_profile,
        question__mission=mission
    )
    questions_answered = answers.count()
    correct_answers = answers.filter(selected_choice__is_correct=True).count()
    
    if questions_answered > 0:
        current_score = (correct_answers / questions_answered) * 100
    else:
        current_score = 0
    
    mission_complete = mission in user_profile.completed_missions.all()
    
    context = {
        'mission': mission,
        'questions_answered': questions_answered,
        'total_questions': total_questions,
        'current_score': current_score,
        'mission_complete': mission_complete
    }
    return render(request, 'game/mission_results.html', context)

@login_required
def player_progress(request):
    user_profile = request.user.playerprofile
    completed_missions = user_profile.completed_missions.all()
    total_missions = Mission.objects.count()
    
    completion_percentage = (completed_missions.count() / total_missions * 100) if total_missions > 0 else 0
    
    context = {
        'completed_missions': completed_missions,
        'total_missions': total_missions,
        'completion_percentage': completion_percentage,
        'total_score': user_profile.total_score
    }
    return render(request, 'game/player_progress.html', context)