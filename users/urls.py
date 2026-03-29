from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, admin_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete-account/', views.delete_account, name='delete_account'),
    # ... (other auth paths)
    
    # Admin Panel
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/user/<int:user_id>/', admin_views.admin_user_reports, name='admin_user_reports'),
    path('admin-dashboard/delete-report/<uuid:report_id>/', admin_views.admin_delete_report, name='admin_delete_report'),
    path('admin-dashboard/delete-linkedin-report/<int:report_id>/', admin_views.admin_delete_linkedin_report, name='admin_delete_linkedin_report'),
    path('admin-dashboard/toggle-block/<int:user_id>/', admin_views.toggle_user_block, name='toggle_user_block'),
    path('admin-dashboard/delete/<int:user_id>/', admin_views.delete_user_admin, name='delete_user_admin'),
    path('blocked/', admin_views.blocked_view, name='blocked'),

    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
