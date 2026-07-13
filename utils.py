import re

# Predefined common technical and soft skills for better extraction
COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go", "rust",
    "html", "css", "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask", "spring", "laravel",
    "sql", "mysql", "postgresql", "mongodb", "redis", "firebase", "oracle", "sqlite",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "bitbucket", "terraform", "ansible",
    "machine learning", "deep learning", "nlp", "ai", "data science", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
    "agile", "scrum", "kanban", "project management", "product management", "jira", "confluence",
    "communication", "leadership", "teamwork", "problem solving", "critical thinking", "adaptability", "time management",
    "ui", "ux", "figma", "adobe xd", "sketch", "photoshop", "illustrator",
    "rest api", "graphql", "microservices", "serverless", "testing", "unit testing", "integration testing", "devops", "cicd"
}

def extract_entities(text):
    text_lower = text.lower()
    found_skills = []
    
    # Check for multi-word skills first
    for skill in [s for s in COMMON_SKILLS if " " in s]:
        if skill in text_lower:
            found_skills.append(skill.title())
            
    # Check for single-word skills using regex for word boundaries
    for skill in [s for s in COMMON_SKILLS if " " not in s]:
        # Escape skill for regex (handles c++, c#)
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill.title())
            
    # Also keep the fallback for words that look like skills but aren't in our list
    # (e.g. niche technologies)
    words = re.findall(r'\b[a-zA-Z][a-zA-Z+.\-]{3,}\b', text)
    stopwords = {
        "and","or","the","with","from","into","your","this","that","have","for",
        "work","project","experience","include","add","details","more","about"
    }
    for w in words:
        if w.lower() not in stopwords and w.lower() not in [s.lower() for s in found_skills]:
            # Simple heuristic: if it's capitalized in the text, it might be a proper noun/skill
            if w[0].isupper() and len(w) < 20:
                found_skills.append(w)

    return {"SKILL": list(set(found_skills))}
