from django.db import models
from django.contrib.auth.models import User
import uuid

class AnalysisReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses', null=True, blank=True)
    github_username = models.CharField(max_length=100)
    
    # Basic Stats
    total_repos = models.IntegerField(default=0)
    total_stars = models.IntegerField(default=0)
    languages = models.JSONField(default=dict)
    account_age_years = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Analysis Results
    score = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    skills = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.github_username} - {self.score}/100 ({self.created_at.strftime('%Y-%m-%d')})"

class LinkedInReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='linkedin_reports', null=True, blank=True)
    full_name = models.CharField(max_length=200)
    headline = models.CharField(max_length=255, blank=True)
    
    # Textual Content
    profile_text = models.TextField()
    
    # Analysis Metrics
    professional_score = models.IntegerField(default=0)
    summary_strength = models.IntegerField(default=0)
    experience_impact = models.IntegerField(default=0)
    keyword_density = models.IntegerField(default=0)
    
    # Detail Lists
    impact_keywords = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    missing_elements = models.JSONField(default=list)
    
    # Advanced Power-Up Fields
    target_jd = models.TextField(blank=True, null=True)
    jd_match_score = models.IntegerField(default=0)
    suggested_headlines = models.JSONField(default=list)
    experience_data = models.JSONField(default=list)  # Stores parsed timeline data
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LinkedIn: {self.full_name} ({self.professional_score}/100)"


class ComparisonHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    developer_one = models.CharField(max_length=100)
    developer_two = models.CharField(max_length=100)
    report_one = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='comp_one')
    report_two = models.ForeignKey(AnalysisReport, on_delete=models.CASCADE, related_name='comp_two')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comparison: {self.developer_one} vs {self.developer_two}"

