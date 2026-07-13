from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import PyPDF2
from utils import extract_entities
import re

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_text_pypdf2(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text.strip()

def compute_match(resume_text, job_desc):
    # Extract skills from both to focus the match on what matters
    resume_skills = set(s.lower() for s in extract_entities(resume_text).get('SKILL', []))
    jd_skills = set(s.lower() for s in extract_entities(job_desc).get('SKILL', []))
    
    # Calculate skill overlap
    if not jd_skills:
        a = set(re.findall(r'\b\w{4,}\b', resume_text.lower()))
        b = set(re.findall(r'\b\w{4,}\b', job_desc.lower()))
        inter = len(a & b)
        union = len(a | b)
        match_score = (inter / union) if union else 0.0
        return {"total": match_score, "skills": 0, "context": match_score}
    
    skill_match = len(resume_skills & jd_skills) / len(jd_skills)
    a = set(re.findall(r'\b\w{4,}\b', resume_text.lower()))
    b = set(re.findall(r'\b\w{4,}\b', job_desc.lower()))
    word_overlap = len(a & b) / len(b) if b else 0
    
    total_score = (skill_match * 0.8) + (word_overlap * 0.2)
    return {
        "total": min(1.0, total_score),
        "skills": skill_match,
        "context": word_overlap
    }

@app.route('/')
def index():
    success = request.args.get('success')
    return render_template('index.html', success=success)

@app.route('/analyze', methods=['POST'])
def analyze():
    resume_file = request.files.get('resume')
    job_desc = request.form.get('job_description', '').strip()

    if not resume_file or not job_desc:
        return "Resume file or job description missing.", 400

    raw_filename = resume_file.filename
    if not raw_filename or not raw_filename.lower().endswith('.pdf'):
        return "Please upload a valid PDF file.", 400

    filename = secure_filename(raw_filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume_file.save(save_path)

    try:
        resume_text = extract_text_pypdf2(save_path)
    except Exception as e:
        return f"Error reading PDF: {str(e)}", 500

    scores = compute_match(resume_text, job_desc)
    match_score = round(scores['total'] * 100, 2)
    skill_match_score = round(scores['skills'] * 100, 2)
    context_score = round(scores['context'] * 100, 2)

    # Entity Extraction
    resume_entities = extract_entities(resume_text)
    resume_skills = set(s.lower() for s in resume_entities.get('SKILL', []))
    
    jd_entities = extract_entities(job_desc)
    jd_skills = set(s.lower() for s in jd_entities.get('SKILL', []))

    matched_skills = sorted(list(jd_skills & resume_skills))
    missing_skills = sorted(list(jd_skills - resume_skills))

    # Dynamic suggestions
    suggestions = []
    
    # Check for missing critical skills from JD
    if missing_skills:
        top_missing = missing_skills[:3]
        suggestions.append(f"Consider adding skills like {', '.join(top_missing)} which are highly relevant to this job.")

    # Check for common resume sections
    resume_lower = resume_text.lower()
    sections = {
        "Experience/Work History": ["experience", "work history", "professional background"],
        "Education": ["education", "degree", "university", "college"],
        "Skills": ["skills", "competencies", "technologies"],
        "Contact Information": ["email", "phone", "linkedin", "address"]
    }
    
    missing_sections = []
    for section, keywords in sections.items():
        if not any(k in resume_lower for k in keywords):
            missing_sections.append(section)
            
    if missing_sections:
        suggestions.append(f"Your resume seems to be missing these key sections: {', '.join(missing_sections)}.")

    if len(resume_text.split()) < 200:
        suggestions.append("Your resume content is a bit thin. Try expanding on your project details or achievements using the STAR method.")

    # Generate sample interview questions based on skills
    interview_questions = []
    if matched_skills:
        top_skill = matched_skills[0].title()
        interview_questions.append(f"Can you describe a challenging project where you utilized {top_skill}?")
    if missing_skills:
        missing_skill = missing_skills[0].title()
        interview_questions.append(f"How would you approach learning {missing_skill} if it were required for a critical task on Day 1?")
    
    interview_questions.append("Tell me about a time you had to handle a conflict within a team environment.")
    interview_questions.append("Where do you see your professional growth heading in the next 2-3 years?")

    return render_template(
        'result.html',
        match_score=match_score,
        skill_match_score=skill_match_score,
        context_score=context_score,
        matched_skills=[s.title() for s in matched_skills],
        missing_skills=[s.title() for s in missing_skills],
        suggestions=suggestions,
        filename=filename,
        interview_questions=interview_questions
    )

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    company = request.form.get('company', '').strip()
    message = request.form.get('message', '').strip()
    if not name or not email or not message:
        return redirect(url_for('index', success='0'))
    contacts_path = os.path.join(app.config['UPLOAD_FOLDER'], 'contact_submissions.csv')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    row = f'"{name}","{email}","{company}","{message.replace("\"", "\\'")}"\n'
    try:
        with open(contacts_path, 'a', encoding='utf-8') as f:
            f.write(row)
        return redirect(url_for('index', success='1'))
    except Exception:
        return redirect(url_for('index', success='0'))

if __name__ == '__main__':
    app.run(debug=True)