from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AnalysisReport, ComparisonHistory, LinkedInReport
from .github_helper import GitHubHelper
from .linkedin_helper import LinkedInHelper
import uuid

def dashboard(request):
    latest_analyses = AnalysisReport.objects.filter(is_public=True).order_by('-created_at')[:5]
    return render(request, 'analyzer/dashboard.html', {'latest_analyses': latest_analyses})

def analyze_user(request):
    if request.method == 'POST':
        input_val = request.POST.get('github_username')
        if not input_val:
            messages.error(request, "Please enter a GitHub username or URL")
            return redirect('dashboard')
        
        helper = GitHubHelper()
        username = helper.extract_username(input_val)
        data = helper.analyze_profile(username)
        
        if not data:
            messages.error(request, f"Could not find GitHub user: {username}")
            return redirect('dashboard')
        
        score = helper.calculate_score(data)
        skills = helper.detect_skills(data)
        weaknesses = helper.detect_weaknesses(data)
        suggestions = helper.get_suggestions(weaknesses, data)
        
        # Privacy setting
        is_public = request.POST.get('is_public') == 'on' if request.user.is_authenticated else True
        
        # Save to DB if user is logged in
        report = AnalysisReport.objects.create(
            user=request.user if request.user.is_authenticated else None,
            github_username=username,
            total_repos=data['total_repos'],
            total_stars=data['total_stars'],
            languages=data['languages'],
            account_age_years=data['account_age_years'],
            score=score,
            is_public=is_public,
            skills=skills,
            weaknesses=weaknesses,
            suggestions=suggestions
        )
        
        return redirect('analysis_result', report_id=report.id)
        
    return render(request, 'analyzer/analyze_form.html')

def analysis_result(request, report_id):
    report = get_object_or_404(AnalysisReport, id=report_id)
    # 282.7 is the circumference of a circle with r=45
    dash_offset = 282.7 - (282.7 * report.score / 100)
    return render(request, 'analyzer/result.html', {'report': report, 'dash_offset': dash_offset})

@login_required
def history(request):
    github_reports = AnalysisReport.objects.filter(user=request.user).order_by('-created_at')
    linkedin_reports = LinkedInReport.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'analyzer/history.html', {
        'github_reports': github_reports,
        'linkedin_reports': linkedin_reports
    })

@login_required
def delete_linkedin_report(request, report_id):
    report = get_object_or_404(LinkedInReport, id=report_id, user=request.user)
    report.delete()
    messages.success(request, "Professional report deleted successfully.")
    return redirect('history')

def compare_users(request):
    if request.method == 'POST':
        user1 = request.POST.get('user1')
        user2 = request.POST.get('user2')
        
        helper = GitHubHelper()
        data1 = helper.analyze_profile(user1)
        data2 = helper.analyze_profile(user2)
        
        if not data1 or not data2:
            messages.error(request, "One or both GitHub usernames are invalid.")
            return redirect('compare')
        
        score1 = helper.calculate_score(data1)
        score2 = helper.calculate_score(data2)
        
        # Create reports for comparison
        report1 = AnalysisReport.objects.create(github_username=user1, score=score1, total_repos=data1['total_repos'], total_stars=data1['total_stars'], languages=data1['languages'], account_age_years=data1['account_age_years'])
        report2 = AnalysisReport.objects.create(github_username=user2, score=score2, total_repos=data2['total_repos'], total_stars=data2['total_stars'], languages=data2['languages'], account_age_years=data2['account_age_years'])
        
        context = {
            'report1': report1,
            'report2': report2,
            'winner': user1 if score1 > score2 else user2 if score2 > score1 else "Tie"
        }
        return render(request, 'analyzer/compare_result.html', context)
        
    return render(request, 'analyzer/compare_form.html')

@login_required
def delete_report(request, report_id):
    report = get_object_or_404(AnalysisReport, id=report_id, user=request.user)
    report.delete()
    messages.success(request, "Report deleted successfully.")
    return redirect('history')

def share_report(request, report_id):
    report = get_object_or_404(AnalysisReport, id=report_id)
    # This just reuses the result template but could have a specific 'shared' view
    return render(request, 'analyzer/result.html', {'report': report, 'is_shared': True})


def analyze_linkedin(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', 'Professional')
        profile_text = request.POST.get('profile_text')
        target_jd = request.POST.get('target_jd', '')
        
        if not profile_text or len(profile_text) < 50:
            messages.error(request, "Please provide a more detailed profile summary (at least 50 characters).")
            return redirect('dashboard')
            
        helper = LinkedInHelper()
        analysis = helper.analyze_profile_text(profile_text, target_jd=target_jd)
        
        if not analysis:
            messages.error(request, "Could not analyze the provided text.")
            return redirect('dashboard')
            
        # Save report
        report = LinkedInReport.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            profile_text=profile_text,
            target_jd=target_jd,
            professional_score=analysis['professional_score'],
            summary_strength=analysis['summary_strength'],
            experience_impact=analysis['experience_impact'],
            keyword_density=analysis['keyword_density'],
            impact_keywords=analysis['impact_keywords'],
            suggestions=analysis['suggestions'],
            jd_match_score=analysis['jd_match_score'],
            suggested_headlines=analysis['suggested_headlines'],
            experience_data=analysis['experience_data']
        )
        
        return redirect('linkedin_result', report_id=report.id)
    return redirect('dashboard')

def linkedin_result(request, report_id):
    report = get_object_or_404(LinkedInReport, id=report_id)
    dash_offset = 282.7 - (282.7 * report.professional_score / 100)
    return render(request, 'analyzer/linkedin_result.html', {
        'report': report, 
        'dash_offset': dash_offset
    })
