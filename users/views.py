from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    from analyzer.models import AnalysisReport
    user_reports = AnalysisReport.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_reports = AnalysisReport.objects.filter(user=request.user).count()

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'p_form': p_form,
        'user_reports': user_reports,
        'total_reports': total_reports
    }
    return render(request, 'users/profile.html', context)

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        user.delete()
        messages.success(request, f"Account '{username}' has been successfully deleted.")
        return redirect('register')
    return redirect('profile')
