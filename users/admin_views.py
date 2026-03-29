from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, AdminActionLog
from analyzer.models import AnalysisReport, LinkedInReport

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_dashboard(request):
    query = request.GET.get('q', '')
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    if query:
        from django.db.models import Q
        users = users.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) | 
            Q(profile__github_username__icontains=query)
        )
    
    total_users = users.count()
    github_reports_count = AnalysisReport.objects.count()
    linkedin_reports_count = LinkedInReport.objects.count()
    total_reports_count = github_reports_count + linkedin_reports_count
    blocked_users_count = Profile.objects.filter(is_blocked=True).count()
    
    # Global Analytics (Technical focused)
    from django.db.models import Avg
    import collections
    
    avg_score = AnalysisReport.objects.aggregate(Avg('score'))['score__avg'] or 0
    
    # Top Languages (Simplified extraction from JSON)
    all_reports = AnalysisReport.objects.all().only('languages')
    lang_counter = collections.Counter()
    for r in all_reports:
        for lang in r.languages.keys():
            lang_counter[lang] += 1
    top_languages = lang_counter.most_common(5)
    
    # Activity Logs
    logs = AdminActionLog.objects.all()[:10]

    context = {
        'users': users,
        'total_users': total_users,
        'total_reports': total_reports_count,
        'github_count': github_reports_count,
        'linkedin_count': linkedin_reports_count,
        'blocked_users': blocked_users_count,
        'avg_score': round(avg_score, 1),
        'top_languages': top_languages,
        'query': query,
        'logs': logs,
    }
    return render(request, 'users/admin/dashboard.html', context)

@user_passes_test(is_staff)
def admin_user_reports(request, user_id):
    user_to_view = get_object_or_404(User, id=user_id)
    github_reports = AnalysisReport.objects.filter(user=user_to_view).order_by('-created_at')
    linkedin_reports = LinkedInReport.objects.filter(user=user_to_view).order_by('-created_at')
    
    context = {
        'user_to_view': user_to_view,
        'github_reports': github_reports,
        'linkedin_reports': linkedin_reports,
    }
    return render(request, 'users/admin/user_reports.html', context)

@user_passes_test(is_staff)
def admin_delete_linkedin_report(request, report_id):
    report = get_object_or_404(LinkedInReport, id=report_id)
    user_id = report.user.id if report.user else None
    name = report.full_name
    
    AdminActionLog.objects.create(
        admin=request.user,
        action=f"Deleted LinkedIn report for {name}"
    )
    
    report.delete()
    messages.success(request, f"LinkedIn report for {name} has been deleted.")
    if user_id:
        return redirect('admin_user_reports', user_id=user_id)
    return redirect('admin_dashboard')

@user_passes_test(is_staff)
def admin_delete_report(request, report_id):
    report = get_object_or_404(AnalysisReport, id=report_id)
    user_id = report.user.id if report.user else None
    username = report.github_username
    
    AdminActionLog.objects.create(
        admin=request.user,
        action=f"Deleted analysis report for @{username}"
    )
    
    report.delete()
    messages.success(request, f"Analysis report for @{username} has been deleted.")
    if user_id:
        return redirect('admin_user_reports', user_id=user_id)
    return redirect('admin_dashboard')

@user_passes_test(is_staff)
def toggle_user_block(request, user_id):
    user_to_manage = get_object_or_404(User, id=user_id)
    if user_to_manage.is_staff:
        messages.error(request, "Cannot block a staff member.")
        return redirect('admin_dashboard')
        
    profile = user_to_manage.profile
    profile.is_blocked = not profile.is_blocked
    profile.save()
    
    status = "blocked" if profile.is_blocked else "unblocked"
    
    AdminActionLog.objects.create(
        admin=request.user,
        action=f"{status.capitalize()} user: {user_to_manage.username}"
    )
    
    messages.success(request, f"User {user_to_manage.username} has been {status}.")
    return redirect('admin_dashboard')

@user_passes_test(is_staff)
def delete_user_admin(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    if user_to_delete.is_staff:
        messages.error(request, "Cannot delete a staff member.")
        return redirect('admin_dashboard')
        
    username = user_to_delete.username
    
    AdminActionLog.objects.create(
        admin=request.user,
        action=f"Deleted user account: {username}"
    )
    
    user_to_delete.delete()
    messages.success(request, f"User {username} and all their data have been deleted.")
    return redirect('admin_dashboard')

def blocked_view(request):
    return render(request, 'users/blocked.html')
