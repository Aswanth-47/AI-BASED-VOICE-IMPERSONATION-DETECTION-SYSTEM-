import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import VoiceAnalysis, UserProfile
from .forms import SignUpForm, LoginForm, AudioUploadForm
from .detector import analyze_audio


# ─── Public Views ────────────────────────────────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/index.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to VoiceGuard AI, {user.first_name}! 🎉')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')


# ─── Protected Views ──────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    recent_analyses = VoiceAnalysis.objects.filter(user=user)[:8]

    # Stats
    total = VoiceAnalysis.objects.filter(user=user).count()
    ai_count = VoiceAnalysis.objects.filter(user=user, result='ai').count()
    human_count = VoiceAnalysis.objects.filter(user=user, result='human').count()
    uncertain_count = VoiceAnalysis.objects.filter(user=user, result='uncertain').count()
    avg_confidence = VoiceAnalysis.objects.filter(user=user).aggregate(
        avg=Avg('confidence_score'))['avg'] or 0

    # Last 7 days activity
    seven_days_ago = timezone.now() - timedelta(days=7)
    weekly_data = []
    for i in range(6, -1, -1):
        day = timezone.now() - timedelta(days=i)
        count = VoiceAnalysis.objects.filter(
            user=user,
            analyzed_at__date=day.date()
        ).count()
        weekly_data.append({'day': day.strftime('%a'), 'count': count})

    context = {
        'profile': profile,
        'recent_analyses': recent_analyses,
        'total': total,
        'ai_count': ai_count,
        'human_count': human_count,
        'uncertain_count': uncertain_count,
        'avg_confidence': round(avg_confidence, 1),
        'weekly_data': json.dumps(weekly_data),
        'upload_form': AudioUploadForm(),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def analyze_audio_view(request):
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = request.FILES['audio_file']
            file_size_kb = round(audio_file.size / 1024, 2)

            # Save analysis record
            analysis = VoiceAnalysis(
                user=request.user,
                audio_file=audio_file,
                file_name=audio_file.name,
                file_size=file_size_kb,
            )
            analysis.save()

            # Run AI detection
            try:
                result_data = analyze_audio(analysis.audio_file.path)
                analysis.result = result_data['result']
                analysis.confidence_score = result_data['confidence_score']
                analysis.duration = result_data['duration']
                analysis.spectral_score = result_data['spectral_score']
                analysis.pitch_score = result_data['pitch_score']
                analysis.rhythm_score = result_data['rhythm_score']
                analysis.noise_score = result_data['noise_score']
                analysis.formant_score = result_data['formant_score']
                analysis.save()
            except Exception as e:
                analysis.result = 'uncertain'
                analysis.confidence_score = 50.0
                analysis.save()

            # Update user profile stats
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.total_analyses += 1
            if analysis.result == 'ai':
                profile.ai_detected += 1
            elif analysis.result == 'human':
                profile.human_detected += 1
            profile.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'result': analysis.result,
                    'confidence_score': analysis.confidence_score,
                    'file_name': analysis.file_name,
                    'duration': analysis.duration,
                    'spectral_score': analysis.spectral_score,
                    'pitch_score': analysis.pitch_score,
                    'rhythm_score': analysis.rhythm_score,
                    'noise_score': analysis.noise_score,
                    'formant_score': analysis.formant_score,
                    'analyzed_at': analysis.analyzed_at.strftime('%b %d, %Y %I:%M %p'),
                    'analysis_id': analysis.id,
                })

            messages.success(request, f'Analysis complete: {analysis.file_name} is {analysis.result.upper()} ({analysis.confidence_score}% confidence)')
            return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = []
                for field, errs in form.errors.items():
                    errors.extend(errs)
                return JsonResponse({'success': False, 'error': ' '.join(errors)}, status=400)
            messages.error(request, 'Invalid file. Please check the format and size.')
            return redirect('dashboard')

    return redirect('dashboard')


@login_required
def analysis_history(request):
    analyses = VoiceAnalysis.objects.filter(user=request.user)
    result_filter = request.GET.get('filter', 'all')
    if result_filter in ['human', 'ai', 'uncertain']:
        analyses = analyses.filter(result=result_filter)

    context = {
        'analyses': analyses,
        'result_filter': result_filter,
        'total': analyses.count(),
    }
    return render(request, 'core/history.html', context)


@login_required
def analysis_detail(request, pk):
    analysis = get_object_or_404(VoiceAnalysis, pk=pk, user=request.user)
    return render(request, 'core/analysis_detail.html', {'analysis': analysis})


@login_required
def delete_analysis(request, pk):
    analysis = get_object_or_404(VoiceAnalysis, pk=pk, user=request.user)
    if request.method == 'POST':
        # Update profile stats
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.total_analyses = max(0, profile.total_analyses - 1)
        if analysis.result == 'ai':
            profile.ai_detected = max(0, profile.ai_detected - 1)
        elif analysis.result == 'human':
            profile.human_detected = max(0, profile.human_detected - 1)
        profile.save()

        if analysis.audio_file and os.path.exists(analysis.audio_file.path):
            os.remove(analysis.audio_file.path)
        analysis.delete()
        messages.success(request, 'Analysis deleted successfully.')
    return redirect('history')
