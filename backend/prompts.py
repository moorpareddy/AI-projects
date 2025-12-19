"""
LLM Prompts for Resume Analysis
Contains carefully crafted prompts with few-shot examples
"""

# System prompts for different analysis stages
SYSTEM_PROMPT = """You are an expert HR analyst and technical recruiter with 15+ years of experience. 
You specialize in resume analysis, candidate evaluation, and ATS optimization. 
You provide accurate, actionable, and honest assessments."""


# ============================================
# 1. RESUME EXTRACTION PROMPT
# ============================================

RESUME_EXTRACTION_PROMPT = """Extract structured information from the following resume.

Analyze the resume text and extract:
1. **Skills**: All technical skills, tools, languages, frameworks, methodologies
2. **Experience Years**: Total years of professional experience (estimate if not explicit)
3. **Education**: Degrees, institutions, certifications
4. **Projects**: Project names and brief descriptions
5. **Certifications**: Professional certifications
6. **Work Experience**: Job titles, companies, and key responsibilities

**IMPORTANT**: 
- Extract skills comprehensively (don't miss any)
- Be specific (e.g., "Python", "React", "AWS", not just "programming")
- For experience, look for dates and calculate total years
- Return valid JSON only

**Example 1:**
Resume: "Senior Software Engineer with 5 years at Google. Skills: Python, Django, PostgreSQL, Docker, AWS. 
Built microservices handling 1M requests/day. MS in Computer Science from Stanford."

Output:
```json
{
  "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS", "Microservices"],
  "experience_years": 5,
  "education": ["MS Computer Science - Stanford University"],
  "projects": ["Microservices architecture handling 1M+ daily requests"],
  "certifications": [],
  "work_experience": ["Senior Software Engineer at Google (5 years)"]
}
```

**Example 2:**
Resume: "Data Scientist, 3 years exp. Skills: Python, TensorFlow, scikit-learn, SQL, Tableau. 
Built ML models for fraud detection. BS in Mathematics. AWS Certified ML Specialty."

Output:
```json
{
  "skills": ["Python", "TensorFlow", "scikit-learn", "SQL", "Tableau", "Machine Learning", "Fraud Detection"],
  "experience_years": 3,
  "education": ["BS in Mathematics"],
  "projects": ["ML models for fraud detection"],
  "certifications": ["AWS Certified Machine Learning - Specialty"],
  "work_experience": ["Data Scientist (3 years)"]
}
```

Now extract from this resume:

{resume_text}

Return ONLY valid JSON with the structure shown above. No additional text."""


# ============================================
# 2. JOB DESCRIPTION EXTRACTION PROMPT
# ============================================

JOB_DESCRIPTION_EXTRACTION_PROMPT = """Extract structured requirements from the following job description.

Analyze and extract:
1. **Required Skills**: Must-have technical skills explicitly stated
2. **Preferred Skills**: Nice-to-have or preferred qualifications
3. **Responsibilities**: Key job responsibilities
4. **Required Experience**: Minimum years of experience needed
5. **Qualifications**: Educational or certification requirements

**IMPORTANT**:
- Distinguish between "required" and "preferred" carefully
- Extract all technical skills mentioned
- Look for phrases like "must have", "required", "3+ years", "preferred"
- Return valid JSON only

**Example 1:**
Job Description: "Seeking Senior Backend Engineer with 5+ years experience. REQUIRED: Python, FastAPI, PostgreSQL, Docker. 
PREFERRED: AWS, Kubernetes. Responsibilities: Design scalable APIs, mentor juniors, deploy microservices. BS in CS required."

Output:
```json
{
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "preferred_skills": ["AWS", "Kubernetes"],
  "responsibilities": [
    "Design and implement scalable APIs",
    "Mentor junior engineers",
    "Deploy and maintain microservices"
  ],
  "required_experience_years": 5,
  "qualifications": ["Bachelor's degree in Computer Science or related field"]
}
```

**Example 2:**
Job Description: "ML Engineer needed. Must have: Python, TensorFlow, PyTorch, 3+ years ML experience. 
Nice to have: MLflow, Kubeflow. Build and deploy ML models. Master's preferred."

Output:
```json
{
  "required_skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning"],
  "preferred_skills": ["MLflow", "Kubeflow"],
  "responsibilities": ["Build and deploy machine learning models"],
  "required_experience_years": 3,
  "qualifications": ["Master's degree preferred"]
}
```

Now extract from this job description:

{job_description}

Return ONLY valid JSON with the structure shown above. No additional text."""


# ============================================
# 3. SKILLS COMPARISON & SCORING PROMPT
# ============================================

SKILLS_COMPARISON_PROMPT = """Compare the candidate's resume against the job requirements and provide a detailed skills analysis.

**Resume Skills:**
{resume_skills}

**Resume Experience:** {resume_experience_years} years

**Job Required Skills:**
{job_required_skills}

**Job Preferred Skills:**
{job_preferred_skills}

**Job Required Experience:** {job_required_experience_years} years

Analyze and return:
1. **matching_skills**: Skills present in resume that match job requirements
2. **missing_required_skills**: Required skills NOT found in resume
3. **missing_preferred_skills**: Preferred skills NOT found in resume
4. **skill_match_percentage**: % of required skills the candidate has (0-100)
5. **skills_match_score**: Score based on skill overlap (0-100)
6. **experience_relevance_score**: Score based on experience match (0-100)

**Scoring Guidelines:**
- skills_match_score: 100 if all required skills present, proportional reduction for missing skills
- experience_relevance_score: 100 if experience >= required, reduce by 10 per year gap if less
- Consider synonyms (e.g., "JS" = "JavaScript", "React.js" = "React")
- Consider related skills (e.g., "TensorFlow" covers some "Deep Learning" need)

Return ONLY valid JSON:
```json
{
  "matching_skills": [],
  "missing_required_skills": [],
  "missing_preferred_skills": [],
  "skill_match_percentage": 0,
  "skills_match_score": 0,
  "experience_relevance_score": 0
}
```"""


# ============================================
# 4. RESUME IMPROVEMENT PROMPT
# ============================================

RESUME_IMPROVEMENT_PROMPT = """As an expert resume coach, provide actionable improvement suggestions for this candidate.

**Resume Context:**
{resume_text}

**Job Description:**
{job_description}

**Current Gaps:**
- Missing Required Skills: {missing_required_skills}
- Missing Preferred Skills: {missing_preferred_skills}
- Match Score: {current_match_score}/100

Provide 5-10 specific, actionable improvement suggestions across these categories:
- **skills**: Technical skills to add or highlight
- **experience**: How to better present experience
- **format**: Resume structure and formatting improvements
- **keywords**: ATS-friendly keywords to include
- **achievements**: How to quantify and strengthen achievements

**Each suggestion must include:**
- category: one of [skills, experience, format, keywords, achievements]
- suggestion: Specific, actionable advice (1-2 sentences)
- priority: high/medium/low based on impact on this job match
- impact: Expected improvement if implemented

**Example Output:**
```json
{
  "suggestions": [
    {
      "category": "skills",
      "suggestion": "Add 'Docker' and 'Kubernetes' prominently in your skills section, as these are required for the role and critical for containerization expertise.",
      "priority": "high",
      "impact": "Could increase match score by 10-15 points and pass ATS screening"
    },
    {
      "category": "achievements",
      "suggestion": "Quantify your API development work - e.g., 'Designed REST APIs serving 50K+ requests/second' instead of just 'Built APIs'.",
      "priority": "high",
      "impact": "Makes accomplishments concrete and impressive to hiring managers"
    },
    {
      "category": "keywords",
      "suggestion": "Include exact phrases from job description like 'microservices architecture' and 'scalable systems' in your experience bullets.",
      "priority": "medium",
      "impact": "Improves ATS keyword matching by 20%"
    }
  ]
}
```

Return ONLY valid JSON with the suggestions array."""


# ============================================
# 5. BULLET POINT OPTIMIZATION PROMPT
# ============================================

BULLET_OPTIMIZATION_PROMPT = """Optimize resume bullet points to better match the job description and improve ATS scoring.

**Job Description Focus:**
{job_description}

**Original Bullet Points:**
{original_bullets}

For each bullet point, create an optimized version that:
1. Incorporates relevant keywords from the job description
2. Follows the STAR method (Situation, Task, Action, Result)
3. Quantifies achievements with metrics where possible
4. Uses strong action verbs
5. Maintains truthfulness (don't fabricate, only enhance presentation)

**Example:**
Original: "Worked on backend development using Python"
Optimized: "Developed scalable backend microservices using Python and FastAPI, serving 100K+ daily active users with 99.9% uptime"
Reason: "Added specific technologies (FastAPI), quantified impact (100K users, 99.9% uptime), and used stronger verb (Developed vs Worked)"

Return ONLY valid JSON:
```json
{
  "optimized_bullets": [
    {
      "original": "string",
      "optimized": "string",
      "improvement_reason": "string"
    }
  ]
}
```"""


# ============================================
# 6. FINAL VERDICT & SUMMARY PROMPT
# ============================================

FINAL_VERDICT_PROMPT = """Based on all analysis, provide a final hiring recommendation and comprehensive summary.

**Analysis Summary:**
- Overall Match Score: {overall_score}/100
- Skills Match: {skills_score}/100
- Experience Relevance: {experience_score}/100
- Semantic Similarity: {similarity_score}/100

**Skills Analysis:**
- Matching Skills: {matching_skills}
- Missing Required Skills: {missing_required_skills}

Generate:
1. **final_verdict**: One of ["Strong Match", "Moderate Match", "Weak Match"]
   - Strong Match: Score >= 75, max 1 missing required skill
   - Moderate Match: Score 50-74, or 2-3 missing required skills
   - Weak Match: Score < 50, or 4+ missing required skills

2. **verdict_explanation**: 2-3 sentence justification for the verdict

3. **key_strengths**: 3-5 strongest points in candidate's favor (specific to this role)

4. **key_weaknesses**: 3-5 main gaps or concerns (specific to this role)

5. **ats_score**: Estimated ATS (Applicant Tracking System) score (0-100)
   - Based on keyword match, formatting, and completeness

**Example:**
```json
{
  "final_verdict": "Strong Match",
  "verdict_explanation": "Candidate possesses 90% of required technical skills with 5 years of directly relevant experience. Strong track record in scalable backend development with quantified achievements. Only minor gap in Kubernetes experience, which can be quickly learned.",
  "key_strengths": [
    "Expert in Python and FastAPI with production experience",
    "Proven ability to design systems handling high traffic (1M+ requests)",
    "Strong mentorship and leadership background",
    "Excellent track record at top-tier companies"
  ],
  "key_weaknesses": [
    "No Kubernetes experience mentioned, though has Docker expertise",
    "Limited cloud architecture certifications",
    "Could better quantify performance improvements in resume"
  ],
  "ats_score": 87
}
```

Return ONLY valid JSON with the structure shown above."""


# ============================================
# RESUME QUALITY ASSESSMENT PROMPT
# ============================================

RESUME_QUALITY_PROMPT = """Assess the overall quality of this resume from a professional hiring perspective.

**Resume Text:**
{resume_text}

Evaluate and score (0-100) based on:
1. **Clarity & Structure**: Well-organized, easy to scan, logical flow
2. **Quantified Achievements**: Uses metrics and numbers to show impact
3. **Action-Oriented Language**: Strong verbs, active voice
4. **Relevant Content**: Focused on relevant experience, no fluff
5. **ATS-Friendliness**: Proper formatting, keyword usage, no graphics/tables that break parsing

Consider:
- Are achievements quantified? (Good: "Reduced latency by 40%", Bad: "Improved performance")
- Is it concise? (Good: 1-2 pages, Bad: 4+ pages with irrelevant details)
- Does it use strong verbs? (Good: "Architected", "Spearheaded", Bad: "Responsible for", "Worked on")
- Is it ATS-compatible? (Good: Clean formatting, Bad: Graphics, multiple columns)

Return ONLY a JSON with:
```json
{
  "resume_quality_score": 85,
  "quality_notes": "Well-structured with quantified achievements. Could improve by adding more specific metrics to older roles."
}
```"""


# Helper function to format prompts
def format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with provided variables"""
    # Use string.Template instead of .format() to avoid issues with curly braces in content
    import string
    # Replace {var} with ${var} for Template compatibility
    template_fixed = template
    for key in kwargs:
        placeholder = "{" + key + "}"
        template_fixed = template_fixed.replace(placeholder, f"${{{key}}}")
    
    template_obj = string.Template(template_fixed)
    return template_obj.safe_substitute(**kwargs)
