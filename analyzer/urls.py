from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analyze/', views.analyze_user, name='analyze'),
    path('result/<uuid:report_id>/', views.analysis_result, name='analysis_result'),
    path('history/', views.history, name='history'),
    path('compare/', views.compare_users, name='compare'),
    path('delete/<uuid:report_id>/', views.delete_report, name='delete_report'),
    path('delete-jd/<uuid:report_id>/', views.delete_jd_report, name='delete_jd_report'),
    path('share/<uuid:report_id>/', views.share_report, name='share_report'),
    path('match-jd/', views.match_jd, name='match_jd'),
    path('match-jd/result/<uuid:report_id>/', views.jd_match_result, name='jd_match_result'),
]
