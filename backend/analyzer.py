"""
Analyzer Module - Core resume analysis and scoring logic
Orchestrates all components to generate comprehensive analysis
"""
import json
import re
from typing import List, Dict

from .config import settings
from .schemas import (
    ResumeData, JobDescriptionData, AnalysisResult, AnalysisScores,
    SkillsComparison, ImprovementSuggestion, OptimizedBulletPoint
)
from .embeddings import SemanticMatcher
from .prompts import (
    SYSTEM_PROMPT, SKILLS_COMPARISON_PROMPT, RESUME_IMPROVEMENT_PROMPT,
    BULLET_OPTIMIZATION_PROMPT, FINAL_VERDICT_PROMPT, RESUME_QUALITY_PROMPT,
    format_prompt
)


class ResumeAnalyzer:
    """Main analyzer that orchestrates the complete analysis pipeline"""
    
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()
        self.llm_provider = settings.llm_provider
        self.weights = settings.get_weights_dict()
    
    def analyze(
        self, 
        resume_data: ResumeData, 
        job_data: JobDescriptionData
    ) -> AnalysisResult:
        """
        Perform complete resume analysis
        
        Args:
            resume_data: Parsed resume information
            job_data: Parsed job description information
            
        Returns:
            Complete analysis result
        """
        # Step 1: Compute semantic similarity
        semantic_result = self.semantic_matcher.match_resume_to_job(
            resume_data.raw_text,
            job_data.raw_text
        )
        semantic_similarity_score = semantic_result["semantic_match_score"]
        
        # Step 2: Skills comparison and scoring
        skills_result = self._analyze_skills(resume_data, job_data)
        
        # Step 3: Experience relevance scoring
        experience_score = self._score_experience_relevance(resume_data, job_data)
        
        # Step 4: Resume quality assessment
        quality_score = self._assess_resume_quality(resume_data)
        
        # Step 5: Calculate overall score (weighted)
        overall_score = self._calculate_overall_score(
            skills_result["skills_match_score"],
            experience_score,
            semantic_similarity_score,
            quality_score
        )
        
        # Step 6: Generate improvement suggestions
        improvement_suggestions = self._generate_improvements(
            resume_data,
            job_data,
            skills_result,
            overall_score
        )
        
        # Step 7: Optimize resume bullet points
        optimized_bullets = self._optimize_bullets(
            resume_data,
            job_data
        )
        
        # Step 8: Generate final verdict
        verdict_data = self._generate_verdict(
            overall_score,
            skills_result,
            experience_score,
            semantic_similarity_score
        )
        
        # Compile results
        analysis_result = AnalysisResult(
            match_score=overall_score,
            scores_breakdown=AnalysisScores(
                skills_match_score=skills_result["skills_match_score"],
                experience_relevance_score=experience_score,
                semantic_similarity_score=semantic_similarity_score,
                resume_quality_score=quality_score,
                overall_score=overall_score
            ),
            skills_comparison=SkillsComparison(
                matching_skills=skills_result["matching_skills"],
                missing_required_skills=skills_result["missing_required_skills"],
                missing_preferred_skills=skills_result["missing_preferred_skills"],
                skill_match_percentage=skills_result["skill_match_percentage"]
            ),
            improvement_suggestions=improvement_suggestions,
            optimized_resume_bullets=optimized_bullets,
            final_verdict=verdict_data["final_verdict"],
            verdict_explanation=verdict_data["verdict_explanation"],
            ats_score=verdict_data.get("ats_score", overall_score),
            key_strengths=verdict_data.get("key_strengths", []),
            key_weaknesses=verdict_data.get("key_weaknesses", [])
        )
        
        return analysis_result
    
    def _analyze_skills(
        self, 
        resume_data: ResumeData, 
        job_data: JobDescriptionData
    ) -> dict:
        """Analyze skills match between resume and job"""
        # Use LLM for intelligent skills comparison
        prompt = format_prompt(
            SKILLS_COMPARISON_PROMPT,
            resume_skills=", ".join(resume_data.skills) if resume_data.skills else "None listed",
            resume_experience_years=resume_data.experience_years or "Not specified",
            job_required_skills=", ".join(job_data.required_skills) if job_data.required_skills else "None",
            job_preferred_skills=", ".join(job_data.preferred_skills) if job_data.preferred_skills else "None",
            job_required_experience_years=job_data.required_experience_years or "Not specified"
        )
        
        try:
            response = self._call_llm(prompt)
            result = self._parse_json_response(response)
            
            return {
                "matching_skills": result.get("matching_skills", []),
                "missing_required_skills": result.get("missing_required_skills", []),
                "missing_preferred_skills": result.get("missing_preferred_skills", []),
                "skill_match_percentage": result.get("skill_match_percentage", 0),
                "skills_match_score": result.get("skills_match_score", 0),
            }
        except Exception as e:
            print(f"Error in skills analysis: {e}")
            # Fallback to basic matching
            return self._fallback_skills_analysis(resume_data, job_data)
    
    def _fallback_skills_analysis(
        self, 
        resume_data: ResumeData, 
        job_data: JobDescriptionData
    ) -> dict:
        """Fallback skills analysis using simple matching"""
        resume_skills_lower = [s.lower() for s in resume_data.skills]
        required_skills_lower = [s.lower() for s in job_data.required_skills]
        preferred_skills_lower = [s.lower() for s in job_data.preferred_skills]
        
        matching_skills = [
            skill for skill in job_data.required_skills 
            if skill.lower() in resume_skills_lower
        ]
        
        missing_required = [
            skill for skill in job_data.required_skills 
            if skill.lower() not in resume_skills_lower
        ]
        
        missing_preferred = [
            skill for skill in job_data.preferred_skills 
            if skill.lower() not in resume_skills_lower
        ]
        
        skill_match_percentage = (
            len(matching_skills) / len(job_data.required_skills) * 100 
            if job_data.required_skills else 0
        )
        
        skills_match_score = min(skill_match_percentage, 100)
        
        return {
            "matching_skills": matching_skills,
            "missing_required_skills": missing_required,
            "missing_preferred_skills": missing_preferred,
            "skill_match_percentage": skill_match_percentage,
            "skills_match_score": skills_match_score,
        }
    
    def _score_experience_relevance(
        self, 
        resume_data: ResumeData, 
        job_data: JobDescriptionData
    ) -> float:
        """Score experience relevance"""
        if not job_data.required_experience_years:
            return 100.0  # No requirement, full score
        
        if not resume_data.experience_years:
            return 50.0  # Unknown experience, middle score
        
        required = job_data.required_experience_years
        actual = resume_data.experience_years
        
        if actual >= required:
            # Has enough experience
            return 100.0
        else:
            # Reduce score by 10 points per year short
            gap = required - actual
            score = 100.0 - (gap * 10)
            return max(score, 0.0)
    
    def _assess_resume_quality(self, resume_data: ResumeData) -> float:
        """Assess overall resume quality"""
        prompt = format_prompt(
            RESUME_QUALITY_PROMPT,
            resume_text=resume_data.raw_text[:3000]  # Limit to prevent token overflow
        )
        
        try:
            response = self._call_llm(prompt)
            result = self._parse_json_response(response)
            return result.get("resume_quality_score", 75.0)
        except Exception as e:
            print(f"Error assessing resume quality: {e}")
            # Fallback heuristic assessment
            return self._fallback_quality_assessment(resume_data)
    
    def _fallback_quality_assessment(self, resume_data: ResumeData) -> float:
        """Simple heuristic-based quality assessment"""
        score = 50.0  # Base score
        
        # Has skills listed
        if len(resume_data.skills) >= 5:
            score += 15
        
        # Has education
        if resume_data.education:
            score += 10
        
        # Has work experience
        if resume_data.work_experience:
            score += 15
        
        # Has projects or certifications
        if resume_data.projects or resume_data.certifications:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_overall_score(
        self,
        skills_score: float,
        experience_score: float,
        semantic_score: float,
        quality_score: float
    ) -> float:
        """Calculate weighted overall score"""
        overall = (
            skills_score * self.weights["skills_match"] +
            experience_score * self.weights["experience_relevance"] +
            semantic_score * self.weights["semantic_similarity"] +
            quality_score * self.weights["resume_quality"]
        )
        
        return round(overall, 2)
    
    def _generate_improvements(
        self,
        resume_data: ResumeData,
        job_data: JobDescriptionData,
        skills_result: dict,
        current_score: float
    ) -> List[ImprovementSuggestion]:
        """Generate improvement suggestions"""
        prompt = format_prompt(
            RESUME_IMPROVEMENT_PROMPT,
            resume_text=resume_data.raw_text[:2000],
            job_description=job_data.raw_text[:2000],
            missing_required_skills=", ".join(skills_result["missing_required_skills"]) or "None",
            missing_preferred_skills=", ".join(skills_result["missing_preferred_skills"]) or "None",
            current_match_score=current_score
        )
        
        try:
            response = self._call_llm(prompt)
            result = self._parse_json_response(response)
            
            suggestions = []
            for item in result.get("suggestions", []):
                suggestions.append(ImprovementSuggestion(
                    category=item["category"],
                    suggestion=item["suggestion"],
                    priority=item["priority"],
                    impact=item["impact"]
                ))
            
            return suggestions
        except Exception as e:
            print(f"Error generating improvements: {e}")
            return self._fallback_improvements(skills_result)
    
    def _fallback_improvements(self, skills_result: dict) -> List[ImprovementSuggestion]:
        """Generate basic improvement suggestions"""
        suggestions = []
        
        if skills_result["missing_required_skills"]:
            suggestions.append(ImprovementSuggestion(
                category="skills",
                suggestion=f"Add these required skills to your resume: {', '.join(skills_result['missing_required_skills'][:3])}",
                priority="high",
                impact="Critical for passing ATS and initial screening"
            ))
        
        if skills_result["missing_preferred_skills"]:
            suggestions.append(ImprovementSuggestion(
                category="skills",
                suggestion=f"Consider adding these preferred skills: {', '.join(skills_result['missing_preferred_skills'][:3])}",
                priority="medium",
                impact="Will strengthen your application"
            ))
        
        suggestions.append(ImprovementSuggestion(
            category="achievements",
            suggestion="Quantify your achievements with specific metrics (e.g., 'increased performance by 40%', 'managed team of 5')",
            priority="high",
            impact="Makes your impact concrete and measurable"
        ))
        
        return suggestions
    
    def _optimize_bullets(
        self,
        resume_data: ResumeData,
        job_data: JobDescriptionData
    ) -> List[OptimizedBulletPoint]:
        """Optimize resume bullet points"""
        # Extract bullet points from work experience
        bullets = []
        for exp in resume_data.work_experience[:3]:  # Top 3 experiences
            # Simple split by common bullet point patterns
            exp_bullets = re.split(r'\n[-•*]\s*', exp)
            bullets.extend([b.strip() for b in exp_bullets if len(b.strip()) > 20][:2])
        
        if not bullets:
            return []
        
        bullets = bullets[:5]  # Limit to 5 bullets
        
        prompt = format_prompt(
            BULLET_OPTIMIZATION_PROMPT,
            job_description=job_data.raw_text[:1500],
            original_bullets="\n".join(f"{i+1}. {b}" for i, b in enumerate(bullets))
        )
        
        try:
            response = self._call_llm(prompt)
            result = self._parse_json_response(response)
            
            optimized = []
            for item in result.get("optimized_bullets", []):
                optimized.append(OptimizedBulletPoint(
                    original=item["original"],
                    optimized=item["optimized"],
                    improvement_reason=item["improvement_reason"]
                ))
            
            return optimized
        except Exception as e:
            print(f"Error optimizing bullets: {e}")
            return []
    
    def _generate_verdict(
        self,
        overall_score: float,
        skills_result: dict,
        experience_score: float,
        semantic_score: float
    ) -> dict:
        """Generate final verdict"""
        prompt = format_prompt(
            FINAL_VERDICT_PROMPT,
            overall_score=overall_score,
            skills_score=skills_result["skills_match_score"],
            experience_score=experience_score,
            similarity_score=semantic_score,
            matching_skills=", ".join(skills_result["matching_skills"]) or "None",
            missing_required_skills=", ".join(skills_result["missing_required_skills"]) or "None"
        )
        
        try:
            response = self._call_llm(prompt)
            result = self._parse_json_response(response)
            return result
        except Exception as e:
            print(f"Error generating verdict: {e}")
            return self._fallback_verdict(overall_score, skills_result)
    
    def _fallback_verdict(self, overall_score: float, skills_result: dict) -> dict:
        """Generate basic verdict"""
        missing_count = len(skills_result["missing_required_skills"])
        
        if overall_score >= 75 and missing_count <= 1:
            verdict = "Strong Match"
            explanation = f"High match score of {overall_score:.0f}% with minimal gaps. Strong candidate for the role."
        elif overall_score >= 50 and missing_count <= 3:
            verdict = "Moderate Match"
            explanation = f"Decent match score of {overall_score:.0f}% with some skill gaps. Could be suitable with training."
        else:
            verdict = "Weak Match"
            explanation = f"Lower match score of {overall_score:.0f}% with significant gaps. May not be the best fit."
        
        return {
            "final_verdict": verdict,
            "verdict_explanation": explanation,
            "key_strengths": skills_result["matching_skills"][:3],
            "key_weaknesses": skills_result["missing_required_skills"][:3],
            "ats_score": overall_score
        }
    
    def _call_llm(self, prompt: str) -> str:
        """Call configured LLM"""
        if self.llm_provider == "openai":
            return self._call_openai(prompt)
        elif self.llm_provider == "gemini":
            return self._call_gemini(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        import openai
        
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        return response.choices[0].message.content
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        import google.generativeai as genai
        
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            model_name=settings.gemini_model
        )
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        
        return response.text
    
    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from LLM response"""
        # Try to find JSON in code blocks
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try to find any JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Try parsing the whole response
        return json.loads(response)
