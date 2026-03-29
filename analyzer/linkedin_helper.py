import re
import collections

class LinkedInHelper:
    def __init__(self):
        # Action verbs that indicate impact and ownership
        self.impact_verbs = [
            'led', 'developed', 'managed', 'created', 'designed', 'implemented', 
            'increased', 'reduced', 'saved', 'negotiated', 'transformed', 
            'pioneered', 'optimized', 'accelerated', 'delivered'
        ]
        
        # Professional keywords to look for
        self.industry_keywords = [
            'strategy', 'leadership', 'analytics', 'management', 'collaborated',
            'startup', 'enterprise', 'full-stack', 'agile', 'scrum', 'backend',
            'frontend', 'architecture', 'cloud', 'deployment', 'saas', 'python',
            'javascript', 'aws', 'docker', 'machine-learning', 'data-science'
        ]

    def analyze_profile_text(self, text, target_jd=None):
        if not text:
            return None
            
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        word_count = len(words)
        
        # 1. Summary Strength
        summary_score = min(100, (word_count / 150) * 100) if word_count > 20 else 20
        
        # 2. Experience Impact
        found_verbs = [v for v in self.impact_verbs if v in text_lower]
        experience_score = min(100, (len(found_verbs) / 5) * 100)
        
        # 3. Keyword Density
        found_keywords = [k for k in self.industry_keywords if k in text_lower]
        keyword_score = min(100, (len(found_keywords) / 6) * 100)
        
        # 4. Detect Numbers (quantifiable results)
        numbers = re.findall(r'\d+%|\d+\s?million|\d+\s?users|\d+\s?percent', text_lower)
        quantifiable_multiplier = 1.2 if numbers else 1.0
        
        # Calculate final professional score
        base_score = (summary_score * 0.3) + (experience_score * 0.4) + (keyword_score * 0.3)
        final_score = min(100, base_score * quantifiable_multiplier)
        
        # 5. Job Description Matcher (Power-Up)
        jd_match_score = 0
        if target_jd:
            jd_lower = target_jd.lower()
            jd_keywords = set(re.findall(r'\w{4,}', jd_lower)) # Filter out small words
            profile_set = set(re.findall(r'\w{4,}', text_lower))
            overlap = jd_keywords.intersection(profile_set)
            if jd_keywords:
                jd_match_score = int((len(overlap) / len(jd_keywords)) * 100 * 1.5) # Weight overlap
                jd_match_score = min(100, jd_match_score)
        
        # 6. Headline Generator (Power-Up)
        headlines = self.generate_headlines(found_keywords, found_verbs)
        
        # 7. Timeline Parser (Power-Up)
        experience_data = self.parse_experience_timeline(text)

        # Generate suggestions
        suggestions = []
        if word_count < 100:
            suggestions.append("Your profile summary is too short. Aim for at least 150-200 words to tell your story.")
        if not numbers:
            suggestions.append("Add quantifiable results (e.g., 'Increased revenue by 20%' or 'Managed 5+ developers').")
        
        return {
            'professional_score': int(final_score),
            'summary_strength': int(summary_score),
            'experience_impact': int(experience_score),
            'keyword_density': int(keyword_score),
            'impact_keywords': list(set(found_verbs + found_keywords)),
            'suggestions': suggestions,
            'jd_match_score': jd_match_score,
            'suggested_headlines': headlines,
            'experience_data': experience_data
        }

    def generate_headlines(self, keywords, verbs):
        top_skills = [k.title() for k in keywords[:3]]
        if not top_skills:
            top_skills = ["Software Professional", "Tech Lead"]
            
        return [
            f"{' | '.join(top_skills)} | Driving Innovation & Scalability",
            f"Senior Specialist in {top_skills[0]} - Focused on delivering high-impact technical solutions",
            f"Transforming Business with {' & '.join(top_skills[:2])} | Achievement-driven Technical Leader"
        ]

    def parse_experience_timeline(self, text):
        # A simple regex to find sequences like "Role... Company... Date"
        # Since we can't do complex NLP, we look for common patterns
        experiences = []
        
        # Simplified parser for professional looking lines
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Simple heuristic: Lines starting with a title or having a date-like pattern
            date_match = re.search(r'(20\d{2}|Present|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', line)
            if date_match and len(line) < 100:
                experiences.append({
                    'title': line[:50] + ("..." if len(line) > 50 else ""),
                    'date': date_match.group(0)
                })
        
        # Sort or filter unique ones
        return experiences[:5] # Limit to top 5
