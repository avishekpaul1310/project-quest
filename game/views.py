from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mission, Question, UserMissionProgress
from django.db.models import Sum

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Start new session and reset progress
            user.userprofile.start_new_session()
            return redirect('game:dashboard')
        else:
            return render(request, 'game/login.html', {'error': 'Invalid credentials'})
    return render(request, 'game/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        # Reset user progress before logout
        profile = request.user.userprofile
        profile.reset_progress()
        
        # Clear session data
        request.session.flush()
        
        # Perform logout
        logout(request)
    
    return redirect('game:login')

@login_required
def dashboard(request):
    missions = Mission.objects.filter(is_active=True).order_by('order')
    progress_data = {
        progress.mission_id: progress 
        for progress in UserMissionProgress.objects.filter(user=request.user)
    }
    
    # Get user profile
    profile = request.user.userprofile
    
    return render(request, 'game/dashboard.html', {
        'missions': missions,
        'progress_data': progress_data,
        'user_profile': profile
    })

@login_required
def mission_learning(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    progress = UserMissionProgress.objects.filter(
        user=request.user,
        mission=mission
    ).first()
    
    return render(request, 'game/mission_learning.html', {
        'mission': mission,
        'progress': progress
    })

@login_required
def take_quiz(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    questions = list(mission.questions.all())
    progress = UserMissionProgress.objects.filter(
        user=request.user,
        mission=mission
    ).first()
    
    current_question_index = request.session.get(f'mission_{mission_id}_question_index', 0)
    last_answer = request.session.get(f'mission_{mission_id}_last_answer', None)
    
    if request.method == 'POST':
        question = questions[current_question_index]
        answer = request.POST.get(f'question_{question.id}')
        
        # Store the answer and its correctness
        request.session[f'mission_{mission_id}_last_answer'] = {
            'answer': answer,
            'is_correct': answer == question.correct_option,
            'explanation': question.explanation,
            'consequence': getattr(question, f'consequence_{answer.lower()}')
        }
        
        if request.POST.get('next_question'):
            # Calculate score and move to next question
            score = 20 if answer == question.correct_option else 0
            
            if not progress:
                progress = UserMissionProgress.objects.create(
                    user=request.user,
                    mission=mission,
                    score=score
                )
            else:
                progress.score += score
                progress.save()
            
            if current_question_index + 1 < len(questions):
                request.session[f'mission_{mission_id}_question_index'] = current_question_index + 1
                request.session[f'mission_{mission_id}_last_answer'] = None
                return redirect('game:take_quiz', mission_id=mission_id)
            else:
                # Mission completed
                progress.completed = True
                progress.save()
                
                # Update user profile
                profile = request.user.userprofile
                profile.total_score += progress.score
                profile.xp_points += mission.xp_reward if progress.score >= 60 else 0
                
                if profile.xp_points >= 300:
                    profile.title = "Royal Project Consultant"
                if profile.xp_points >= 600:
                    profile.title = "King's Chief Project Manager"
                profile.save()
                
                # Safely clear session data
                try:
                    del request.session[f'mission_{mission_id}_question_index']
                except KeyError:
                    pass
                    
                try:
                    del request.session[f'mission_{mission_id}_last_answer']
                except KeyError:
                    pass
                
                return redirect('game:mission_results', mission_id=mission_id)
        
        return render(request, 'game/take_quiz.html', {
            'mission': mission,
            'question': question,
            'question_number': current_question_index + 1,
            'total_questions': len(questions),
            'answer_result': request.session[f'mission_{mission_id}_last_answer']
        })
    
    # If there are no more questions, redirect to results
    if current_question_index >= len(questions):
        return redirect('game:mission_results', mission_id=mission_id)
    
    current_question = questions[current_question_index]
    return render(request, 'game/take_quiz.html', {
        'mission': mission,
        'question': current_question,
        'question_number': current_question_index + 1,
        'total_questions': len(questions),
        'answer_result': last_answer
    })

@login_required
def mission_results(request, mission_id):
    mission = get_object_or_404(Mission, pk=mission_id)
    progress = get_object_or_404(UserMissionProgress, 
        user=request.user,
        mission=mission
    )
    
    return render(request, 'game/mission_results.html', {
        'mission': mission,
        'progress': progress
    })