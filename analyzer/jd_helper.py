import re

class JDHelper:
    def __init__(self):
        # Action verbs that indicate impact and ownership
        self.impact_verbs = [
            'led', 'developed', 'managed', 'created', 'designed', 'implemented', 
            'increased', 'reduced', 'saved', 'negotiated', 'transformed', 
            'pioneered', 'optimized', 'accelerated', 'delivered'
        ]
        
        # Professional keywords to look for if JD is sparse
        self.common_tech_skills = [
            'python', 'javascript', 'react', 'django', 'node', 'aws', 'docker',
            'kubernetes', 'sql', 'nosql', 'mongodb', 'postgresql', 'java', 'c++',
            'typescript', 'angular', 'vue', 'cloud', 'devops', 'agile', 'scrum'
        ]

    def extract_keywords(self, text):
        if not text:
            return set()
        # Find words with 3 or more characters, excluding common stop words could be better but let's keep it simple
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        return set(words)

    def match_jd(self, summary, jd):
        if not summary or not jd:
            return None
            
        summary_keywords = self.extract_keywords(summary)
        jd_keywords = self.extract_keywords(jd)
        
        # Filter JD keywords to keep only "significant" ones (length > 3)
        # and maybe some common tech skills if they exist
        significant_jd_keywords = {k for k in jd_keywords if len(k) > 3}
        
        if not significant_jd_keywords:
            return {
                'match_score': 0,
                'matched_skills': [],
                'missing_skills': [],
                'suggestions': ["The job description seems too short to analyze."]
            }
            
        matched = summary_keywords.intersection(significant_jd_keywords)
        missing = significant_jd_keywords - summary_keywords
        
        # Calculate score
        # We can weight the match. If 50% of JD keywords are in summary, that's pretty good.
        match_ratio = len(matched) / len(significant_jd_keywords)
        score = min(100, int(match_ratio * 150)) # multiplier to make it more generous
        
        # Identify Skill Gaps (top 10 missing)
        # We can prioritize tech skills from our list if they are in the missing set
        prioritized_missing = [m for m in missing if m in self.common_tech_skills]
        other_missing = [m for m in missing if m not in self.common_tech_skills]
        
        skill_gaps = (prioritized_missing + other_missing)[:10]
        
        # Suggestions
        suggestions = []
        if score < 50:
            suggestions.append("Your summary is missing several key requirements from the job description.")
        if len(summary.split()) < 50:
            suggestions.append("Consider expanding your summary to at least 100 words to include more relevant keywords.")
        if prioritized_missing:
            suggestions.append(f"Try to incorporate skills like {', '.join(prioritized_missing[:3])} if you have experience with them.")
            
        return {
            'match_score': score,
            'matched_skills': list(matched)[:15],
            'missing_skills': skill_gaps,
            'suggestions': suggestions
        }
