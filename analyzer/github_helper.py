import requests

class GitHubHelper:
    BASE_URL = "https://api.github.com"

    def __init__(self, token=None):
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def extract_username(self, input_str):
        if "github.com/" in input_str:
            # Handle URLs like https://github.com/username or github.com/username
            parts = input_str.split("github.com/")[-1].split("/")
            return parts[0]
        return input_str.strip()

    def get_user_data(self, username):
        response = requests.get(f"{self.BASE_URL}/users/{username}", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_user_repos(self, username):
        repos = []
        page = 1
        while True:
            response = requests.get(f"{self.BASE_URL}/users/{username}/repos?per_page=100&page={page}", headers=self.headers)
            if response.status_code != 200:
                break
            
            page_repos = response.json()
            if not page_repos:
                break
            
            repos.extend(page_repos)
            if len(page_repos) < 100:
                break
            page += 1
            
        return repos

    def analyze_profile(self, username):
        user_data = self.get_user_data(username)
        if not user_data:
            return None

        repos = self.get_user_repos(username)
        
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
        languages_count = {}
        
        for repo in repos:
            lang = repo.get("language")
            if lang:
                languages_count[lang] = languages_count.get(lang, 0) + 1

        # Calculate Account Age
        from datetime import datetime
        created_at = datetime.strptime(user_data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.now()
        age_years = (now - created_at).days / 365.25

        # Detect Django specifically
        has_django = any(
            "django" in repo.get("name", "").lower() or 
            "django" in (repo.get("description") or "").lower()
            for repo in repos
        )

        return {
            "username": username,
            "total_repos": len(repos),
            "total_stars": total_stars,
            "languages": languages_count,
            "account_age_years": round(age_years, 2),
            "avatar_url": user_data.get("avatar_url"),
            "has_django": has_django
        }

    def calculate_score(self, data):
        score = 0
        
        # Repo Count (Max 25 points)
        repo_count = data["total_repos"]
        if repo_count >= 20: score += 25
        elif repo_count >= 10: score += 15
        elif repo_count >= 5: score += 10
        else: score += 5

        # Stars (Max 25 points)
        stars = data["total_stars"]
        if stars >= 100: score += 25
        elif stars >= 50: score += 15
        elif stars >= 10: score += 10
        else: score += 5

        # Tech Diversity (Max 25 points)
        tech_count = len(data["languages"])
        if tech_count >= 5: score += 25
        elif tech_count >= 3: score += 15
        elif tech_count >= 2: score += 10
        else: score += 5

        # Account Age / Consistency (Max 25 points)
        age = data["account_age_years"]
        if age >= 3: score += 25
        elif age >= 1: score += 15
        else: score += 5

        return score

    def detect_skills(self, data):
        languages = data.get('languages', {})
        total_bytes = sum(languages.values())
        if total_bytes == 0: return []
        
        skills = []
        for lang, count in languages.items():
            percentage = (count / total_bytes) * 100
            if percentage < 10: continue  # Must be at least 10% of total code
            
            l_low = lang.lower()
            if l_low in ['python', 'django', 'flask']: skills.append("Backend (Python)")
            if l_low in ['javascript', 'js', 'react', 'vue', 'angular']: skills.append("Frontend (JS)")
            if l_low in ['html', 'css']: skills.append("Web Basics")
            if l_low in ['java', 'kotlin']: skills.append("Mobile/Enterprise (Java)")
            if l_low in ['swift']: skills.append("iOS Development")
        
        if data.get('has_django'):
            skills.append("Django Specialist")
            
        return list(set(skills))

    def detect_weaknesses(self, data):
        weaknesses = []
        if data["total_repos"] < 10: weaknesses.append("Low project volume")
        if data["total_stars"] < 5: weaknesses.append("Low project engagement (stars)")
        if len(data["languages"]) < 3: weaknesses.append("Limited technology stack diversity")
        if data["account_age_years"] < 1: weaknesses.append("New GitHub account")
        return weaknesses

    def get_suggestions(self, weaknesses, data):
        suggestions = []
        has_django = data.get('has_django', False)
        
        for w in weaknesses:
            if "Low project volume" in w: suggestions.append("Build 5 more full-stack projects")
            if "Low project engagement" in w: suggestions.append("Improve README documentation to attract stars")
            if "Limited technology stack" in w:
                if has_django:
                    suggestions.append("Try learning a modern frontend framework like React or Vue.js")
                elif any(lang.lower() == 'python' for lang in data.get('languages', {})):
                    suggestions.append("Expand your Python skills with Django or FastAPI")
                else:
                    suggestions.append("Try learning a new framework like Django or React")
            if "New GitHub account" in w: suggestions.append("Maintain consistent daily commits to build history")
        
        if not suggestions:
            if has_django:
                suggestions.append("Explore Advanced Django (Channels, Rest Framework)")
            suggestions.append("Contribute to open-source projects")
        
        return suggestions

        return suggestions
