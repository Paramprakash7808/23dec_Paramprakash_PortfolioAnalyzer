from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analyze/', views.analyze_user, name='analyze'),
    path('result/<uuid:report_id>/', views.analysis_result, name='analysis_result'),
    path('history/', views.history, name='history'),
    path('compare/', views.compare_users, name='compare'),
    path('delete/<uuid:report_id>/', views.delete_report, name='delete_report'),
    path('delete-linkedin/<int:report_id>/', views.delete_linkedin_report, name='delete_linkedin_report'),
    path('share/<uuid:report_id>/', views.share_report, name='share_report'),
    path('linkedin/', views.analyze_linkedin, name='analyze_linkedin'),
    path('linkedin/result/<int:report_id>/', views.linkedin_result, name='linkedin_result'),
]
