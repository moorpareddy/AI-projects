"""
Pydantic schemas for request/response validation
Defines data structures for resume analysis pipeline
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ResumeData(BaseModel):
    """Extracted resume information"""
    raw_text: str
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    education: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    work_experience: List[str] = Field(default_factory=list)


class JobDescriptionData(BaseModel):
    """Extracted job description information"""
    raw_text: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    required_experience_years: Optional[float] = None
    qualifications: List[str] = Field(default_factory=list)


class SkillsComparison(BaseModel):
    """Skills matching analysis"""
    matching_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    skill_match_percentage: float = Field(ge=0, le=100)


class AnalysisScores(BaseModel):
    """Detailed scoring breakdown"""
    skills_match_score: float = Field(ge=0, le=100)
    experience_relevance_score: float = Field(ge=0, le=100)
    semantic_similarity_score: float = Field(ge=0, le=100)
    resume_quality_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)


class ImprovementSuggestion(BaseModel):
    """Single improvement suggestion"""
    category: Literal["skills", "experience", "format", "keywords", "achievements"]
    suggestion: str
    priority: Literal["high", "medium", "low"]
    impact: str


class OptimizedBulletPoint(BaseModel):
    """Optimized resume bullet point"""
    original: str
    optimized: str
    improvement_reason: str


class AnalysisResult(BaseModel):
    """Complete analysis result returned by the analyzer"""
    match_score: float = Field(ge=0, le=100, description="Overall match score")
    scores_breakdown: AnalysisScores
    skills_comparison: SkillsComparison
    improvement_suggestions: List[ImprovementSuggestion] = Field(default_factory=list)
    optimized_resume_bullets: List[OptimizedBulletPoint] = Field(default_factory=list)
    final_verdict: Literal["Strong Match", "Moderate Match", "Weak Match"]
    verdict_explanation: str
    ats_score: Optional[float] = Field(default=None, ge=0, le=100)
    key_strengths: List[str] = Field(default_factory=list)
    key_weaknesses: List[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    """API request for resume analysis"""
    resume_text: str
    job_description: str


class AnalyzeResponse(BaseModel):
    """API response for resume analysis"""
    success: bool
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None
    processing_time_seconds: Optional[float] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    llm_provider: str
    embedding_provider: str
    api_configured: bool
