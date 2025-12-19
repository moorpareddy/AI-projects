"""
FastAPI Backend - REST API for Resume Analysis
Provides endpoints for resume upload, analysis, and health checks
"""
import time
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .schemas import AnalyzeRequest, AnalyzeResponse, HealthCheckResponse
from .resume_parser import ResumeParser
from .job_parser import JobParser
from .analyzer import ResumeAnalyzer


# Initialize FastAPI app
app = FastAPI(
    title="Resume Analyzer API",
    description="AI-powered resume analysis and job matching API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
resume_parser = ResumeParser()
job_parser = JobParser()
analyzer = ResumeAnalyzer()


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Resume Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns API status and configuration info
    """
    api_configured = False
    
    try:
        settings.validate_api_keys()
        api_configured = True
    except ValueError:
        pass
    
    return HealthCheckResponse(
        status="healthy",
        llm_provider=settings.llm_provider,
        embedding_provider=settings.embedding_provider,
        api_configured=api_configured
    )


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_resume(
    resume_file: UploadFile = File(..., description="Resume PDF file"),
    job_description: str = Form(..., description="Job description text")
):
    """
    Analyze resume against job description
    
    Args:
        resume_file: Uploaded resume PDF
        job_description: Job description text
        
    Returns:
        Comprehensive analysis result with match score, skills comparison, and suggestions
    """
    start_time = time.time()
    
    try:
        # Validate file type
        if not resume_file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Validate file size
        file_content = await resume_file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > settings.max_resume_size_mb:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum of {settings.max_resume_size_mb}MB"
            )
        
        # Validate job description
        if not job_description or len(job_description.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Job description is too short or empty"
            )
        
        # Parse resume
        try:
            resume_data = resume_parser.parse_resume(file_content)
        except Exception as e:
            print(f"ERROR parsing resume: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse resume: {str(e)}"
            )
        
        # Parse job description
        try:
            job_data = job_parser.parse_job_description(job_description)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse job description: {str(e)}"
            )
        
        # Perform analysis
        try:
            analysis_result = analyzer.analyze(resume_data, job_data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return AnalyzeResponse(
            success=True,
            result=analysis_result,
            error=None,
            processing_time_seconds=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalyzeResponse(
            success=False,
            result=None,
            error=str(e),
            processing_time_seconds=round(time.time() - start_time, 2)
        )


@app.post("/analyze-text", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_resume_text(request: AnalyzeRequest):
    """
    Analyze resume text (not PDF) against job description
    Useful for testing or when resume is already in text format
    
    Args:
        request: Contains resume_text and job_description
        
    Returns:
        Comprehensive analysis result
    """
    start_time = time.time()
    
    try:
        # Validate inputs
        if not request.resume_text or len(request.resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text is too short or empty"
            )
        
        if not request.job_description or len(request.job_description.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Job description is too short or empty"
            )
        
        # Parse resume text (skip PDF extraction)
        from .schemas import ResumeData
        resume_data = ResumeData(raw_text=request.resume_text)
        
        # Use LLM to extract structured data
        structured_data = resume_parser._extract_structured_data(request.resume_text)
        resume_data.skills = structured_data.get("skills", [])
        resume_data.experience_years = structured_data.get("experience_years")
        resume_data.education = structured_data.get("education", [])
        resume_data.projects = structured_data.get("projects", [])
        resume_data.certifications = structured_data.get("certifications", [])
        resume_data.work_experience = structured_data.get("work_experience", [])
        
        # Parse job description
        job_data = job_parser.parse_job_description(request.job_description)
        
        # Perform analysis
        analysis_result = analyzer.analyze(resume_data, job_data)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return AnalyzeResponse(
            success=True,
            result=analysis_result,
            error=None,
            processing_time_seconds=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalyzeResponse(
            success=False,
            result=None,
            error=str(e),
            processing_time_seconds=round(time.time() - start_time, 2)
        )


@app.get("/config", tags=["Configuration"])
async def get_config():
    """
    Get current configuration (non-sensitive information only)
    """
    return {
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "scoring_weights": settings.get_weights_dict(),
        "max_file_size_mb": settings.max_resume_size_mb
    }


def start_server():
    """Start the FastAPI server"""
    print(f"""
    ╔═══════════════════════════════════════════════╗
    ║     Resume Analyzer API Starting...          ║
    ╚═══════════════════════════════════════════════╝
    
    🚀 Server: http://{settings.backend_host}:{settings.backend_port}
    📚 Docs: http://{settings.backend_host}:{settings.backend_port}/docs
    🔧 LLM Provider: {settings.llm_provider}
    📊 Embedding Provider: {settings.embedding_provider}
    """)
    
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
