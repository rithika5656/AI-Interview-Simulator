"""Rule-based resume parser for HireVision fallback analysis."""

import re
from typing import Any

def parse_resume(text: str) -> dict[str, Any]:
    """
    Parses resume text using regular expressions and heuristics.
    Extracts name, email, phone, skills, education, experience,
    projects, certifications, achievements, internships, and languages.
    Also calculates a dynamic ATS score based on keywords and completeness.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 1. Extract Email
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else ""
    
    # 2. Extract Phone
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else ""
    
    # 3. Extract Name
    # Heuristic: the first line that doesn't contain common contact info or keywords
    name = "Demo Student"
    for line in lines[:5]:
        if not re.search(email_pattern, line) and not re.search(phone_pattern, line) and len(line) < 50:
            if not any(kw in line.lower() for kw in ["resume", "curriculum", "cv", "profile", "contact", "summary"]):
                name = line
                break

    # 4. Extract Skills
    skill_bank = [
        "python", "java", "c++", "c#", "ruby", "golang", "rust", "php", "typescript", "javascript",
        "html", "css", "react", "angular", "vue", "node", "express", "django", "flask", "fastapi",
        "sql", "mysql", "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure",
        "git", "ci/cd", "machine learning", "deep learning", "nlp", "opencv", "tensorflow", "pytorch",
        "data structures", "algorithms", "system design", "agile", "scrum", "testing", "junit", "selenium",
        "communication", "leadership", "problem solving", "teamwork"
    ]
    lower_text = text.lower()
    skills = []
    for skill in skill_bank:
        # Match word boundaries for skill
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, lower_text):
            # Format nicely
            formatted = skill.title()
            if formatted == "C++":
                formatted = "C++"
            elif formatted == "Ci/Cd":
                formatted = "CI/CD"
            elif formatted == "Nlp":
                formatted = "NLP"
            elif formatted == "Aws":
                formatted = "AWS"
            elif formatted == "Gcp":
                formatted = "GCP"
            elif formatted == "Html":
                formatted = "HTML"
            elif formatted == "Css":
                formatted = "CSS"
            elif formatted == "Dbms":
                formatted = "DBMS"
            elif formatted == "Sql":
                formatted = "SQL"
            skills.append(formatted)
    
    # 5. Extract Sections (Heuristics)
    education = []
    experience = []
    projects = []
    certifications = []
    achievements = []
    internships = []
    languages = []
    
    current_section = None
    
    section_headers = {
        "education": ["education", "academic profile", "qualification", "academic background"],
        "experience": ["experience", "work history", "employment", "professional background"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "certifications": ["certifications", "certificates", "courses"],
        "achievements": ["achievements", "awards", "honors", "accomplishments"],
        "internships": ["internships", "intern experience", "internship details"],
        "languages": ["languages", "languages spoken", "known languages"]
    }
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if line is a section header
        header_found = False
        for sec, keywords in section_headers.items():
            if any(line_lower == kw or line_lower.startswith(kw + " ") or line_lower.endswith(" " + kw) for kw in keywords):
                current_section = sec
                header_found = True
                break
        
        if header_found:
            continue
            
        if current_section:
            # Clean up line
            clean_line = re.sub(r'^[•\-\*]\s*', '', line).strip()
            if not clean_line:
                continue
            
            if current_section == "education" and len(education) < 5:
                education.append(clean_line)
            elif current_section == "experience" and len(experience) < 5:
                experience.append(clean_line)
            elif current_section == "projects" and len(projects) < 5:
                projects.append(clean_line)
            elif current_section == "certifications" and len(certifications) < 5:
                certifications.append(clean_line)
            elif current_section == "achievements" and len(achievements) < 5:
                achievements.append(clean_line)
            elif current_section == "internships" and len(internships) < 5:
                internships.append(clean_line)
            elif current_section == "languages" and len(languages) < 5:
                languages.append(clean_line)

    # 6. Fallback if sections were not populated (simple keyword extraction from paragraphs)
    if not education:
        edu_keywords = ["b.tech", "btech", "m.tech", "mtech", "b.e", "be", "b.sc", "bsc", "bca", "mca", "university", "college", "school"]
        for line in lines:
            if any(kw in line.lower() for kw in edu_keywords) and len(education) < 3:
                education.append(line)
                
    if not projects:
        # Grab lines with project-like descriptions
        for line in lines:
            if any(kw in line.lower() for kw in ["developed", "implemented", "built", "designed", "created"]) and len(projects) < 3:
                projects.append(line)
                
    if not certifications:
        cert_keywords = ["certified", "certification", "certificate", "credential"]
        for line in lines:
            if any(kw in line.lower() for kw in cert_keywords) and len(certifications) < 3:
                certifications.append(line)

    if not languages:
        lang_keywords = ["english", "hindi", "spanish", "french", "german", "telugu", "tamil", "kannada", "marathi"]
        found_langs = [l.title() for l in lang_keywords if l in lower_text]
        languages = found_langs[:4] if found_langs else ["English"]

    # 7. Calculate Dynamic ATS Score
    score = 45.0  # Base score
    
    # Completeness (up to 35 points)
    if email: score += 5
    if phone: score += 5
    if skills: score += 10
    if education: score += 5
    if experience or internships: score += 5
    if projects: score += 5
    
    # Skills count (up to 15 points)
    score += min(15, len(skills) * 1.5)
    
    # Keywords matching check
    missing_keywords = [kw.title() for kw in ["Docker", "System Design", "Kubernetes", "AWS", "Git", "Testing", "CI/CD"] if kw.lower() not in lower_text]
    score += (7 - len(missing_keywords)) * 2
    
    # Formatting (length check)
    word_count = len(text.split())
    if word_count > 300:
        score += 5
    elif word_count < 100:
        score -= 10
        
    ats_score = round(max(10.0, min(100.0, score)), 1)
    
    # 8. Generate dynamic recommendations / suggestions
    suggestions = []
    if not email or not phone:
        suggestions.append("Add clear contact information (Email and Phone) to the top of your resume.")
    if len(skills) < 5:
        suggestions.append("Add more core technical skills and keyword proficiencies to pass ATS filters.")
    if not experience and not internships:
        suggestions.append("Include any internship, freelance work, or open-source contribution to show practical experience.")
    if not projects:
        suggestions.append("Add 2-3 detailed projects with Github links demonstrating your tech stack.")
    if missing_keywords:
        suggestions.append(f"Incorporate missing industry keywords like: {', '.join(missing_keywords[:3])}.")
    if word_count < 150:
        suggestions.append("Expand your resume content with details on project roles, technologies used, and academic metrics.")
    if not suggestions:
        suggestions = ["Optimize resume spacing and layout.", "Include metrics to quantify achievements (e.g., 'improved latency by 20%')."]
        
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education or ["Degree information detected"],
        "experience": experience or ["Work experience details"],
        "projects": projects or ["Project details"],
        "certifications": certifications or ["No certifications explicitly detected"],
        "achievements": achievements or ["Academic / programming achievements"],
        "internships": internships or ["Internship details"],
        "languages": languages,
        "ats_score": ats_score,
        "missing_keywords": missing_keywords[:5],
        "suggestions": suggestions[:4]
    }
