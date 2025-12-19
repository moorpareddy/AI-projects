# 📄 Resume Analyzer & Job Matcher

A production-ready, AI-powered resume analysis and job matching system that provides comprehensive insights, match scoring, and actionable recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Features

### Core Capabilities
- ✅ **Smart Resume Parsing** - Extract skills, experience, education from PDF resumes
- 🎯 **Match Scoring** - AI-powered scoring (0-100) with detailed breakdown
- 🔍 **Skills Analysis** - Identify matching and missing skills
- 💡 **Improvement Suggestions** - Actionable, prioritized recommendations
- ✨ **Resume Optimization** - Enhanced bullet points for ATS compatibility
- 🤖 **ATS Score Simulation** - Estimate Applicant Tracking System performance
- 📊 **Semantic Similarity** - Deep learning-based contextual matching

### Analysis Components
1. **Skills Match (40%)** - Technical and soft skills comparison
2. **Experience Relevance (30%)** - Years of experience and role alignment
3. **Semantic Similarity (20%)** - AI embedding-based contextual match
4. **Resume Quality (10%)** - Format, clarity, quantified achievements

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Streamlit)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  File Upload │  │  Job Input   │  │  Results UI  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST API
┌───────────────────────────▼─────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    API Endpoints                        │ │
│  │  /analyze  |  /analyze-text  |  /health  |  /config   │ │
│  └──────────────────────┬─────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────▼─────────────────────────────────┐ │
│  │                  Analysis Pipeline                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │ │
│  │  │Resume Parser │  │  Job Parser  │  │  Analyzer   │  │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │ │
│  │  ┌──────────────┐  ┌──────────────┐                   │ │
│  │  │  Embeddings  │  │   Prompts    │                   │ │
│  │  └──────────────┘  └──────────────┘                   │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      AI Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   OpenAI     │  │    Gemini    │  │ Transformers │      │
│  │   GPT-4      │  │  Gemini-Pro  │  │  (Local)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
resume-analyzer/
│
├── backend/                      # FastAPI backend
│   ├── __init__.py
│   ├── main.py                   # FastAPI app & endpoints
│   ├── config.py                 # Configuration management
│   ├── schemas.py                # Pydantic models
│   ├── prompts.py                # LLM prompts with few-shot examples
│   ├── resume_parser.py          # PDF parsing & resume extraction
│   ├── job_parser.py             # Job description parsing
│   ├── embeddings.py             # Semantic similarity & embeddings
│   └── analyzer.py               # Core analysis & scoring logic
│
├── frontend/                     # Streamlit frontend
│   └── app.py                    # Interactive UI
│
├── sample_data/                  # Sample files
│   ├── sample_resume.pdf         # Example resume (to be added)
│   └── sample_job_description.txt # Example job posting
│
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── run.sh                        # Linux/Mac startup script
├── run.ps1                       # Windows startup script
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- OpenAI API key OR Google Gemini API key
- 10MB+ disk space
- Internet connection

### Installation

#### 1. Clone or Download the Project
```bash
cd resume_analyser
```

#### 2. Set Up Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here

# For Gemini:
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 3. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Using the Run Script (Recommended)

**Windows (PowerShell):**
```powershell
.\run.ps1
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

#### Option 2: Manual Start

**Terminal 1 - Start Backend:**
```bash
python -m backend.main
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run frontend/app.py
```

### Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### Step-by-Step Process

1. **Open the Web Interface**
   - Navigate to http://localhost:8501 in your browser

2. **Upload Your Resume**
   - Click "Upload Resume" and select your PDF file
   - Supported format: PDF only (max 10MB)

3. **Paste Job Description**
   - Copy the job posting from the company website
   - Paste it into the "Job Description" text area

4. **Analyze**
   - Click the "🚀 Analyze Resume" button
   - Wait 30-60 seconds for AI processing

5. **Review Results**
   - Overall match score (0-100)
   - Score breakdown by category
   - Skills comparison (matching vs. missing)
   - Improvement suggestions
   - Optimized resume bullets
   - Final hiring verdict

## 🔧 Configuration

### Environment Variables

Edit the `.env` file to customize:

```bash
# LLM Provider Selection
LLM_PROVIDER=openai              # Options: openai, gemini, local

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Gemini Configuration
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro

# Embedding Provider
EMBEDDING_PROVIDER=openai        # Options: openai, sentence-transformers

# Scoring Weights (must sum to 1.0)
WEIGHT_SKILLS_MATCH=0.40
WEIGHT_EXPERIENCE_RELEVANCE=0.30
WEIGHT_SEMANTIC_SIMILARITY=0.20
WEIGHT_RESUME_QUALITY=0.10

# Server Settings
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

## 📊 How Scoring Works

### Overall Match Score Formula

```
Overall Score = (Skills × 0.40) + (Experience × 0.30) + 
                (Semantic × 0.20) + (Quality × 0.10)
```

### Component Scores

#### 1. Skills Match Score (40%)
- Compares resume skills vs. required skills
- Uses exact matching + semantic similarity
- Considers synonyms (e.g., "JS" = "JavaScript")
- Formula: `(Matching Skills / Required Skills) × 100`

#### 2. Experience Relevance (30%)
- Compares years of experience
- Full score if resume >= required years
- Reduces by 10 points per year gap if less

#### 3. Semantic Similarity (20%)
- AI embedding-based comparison
- Measures contextual alignment
- Uses cosine similarity (0-1 scaled to 0-100)

#### 4. Resume Quality (10%)
- Evaluates structure, clarity, metrics
- Checks for quantified achievements
- Assesses ATS-friendliness

### Verdict Categories

| Score Range | Verdict | Meaning |
|------------|---------|---------|
| 75-100 | **Strong Match** 🌟 | Excellent fit, highly recommended |
| 50-74 | **Moderate Match** ⭐ | Decent fit, some gaps to address |
| 0-49 | **Weak Match** 💫 | Significant gaps, may not be best fit |

## 🎨 Sample Output

```json
{
  "match_score": 82,
  "scores_breakdown": {
    "skills_match_score": 85,
    "experience_relevance_score": 100,
    "semantic_similarity_score": 75,
    "resume_quality_score": 80
  },
  "skills_comparison": {
    "matching_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "missing_required_skills": ["Kubernetes"],
    "missing_preferred_skills": ["GraphQL"],
    "skill_match_percentage": 80
  },
  "final_verdict": "Strong Match",
  "verdict_explanation": "Candidate possesses 80% of required skills...",
  "ats_score": 87,
  "key_strengths": [
    "Expert in Python and FastAPI",
    "5 years of relevant backend experience",
    "Strong database skills with PostgreSQL"
  ],
  "key_weaknesses": [
    "No Kubernetes experience mentioned",
    "Could add more quantified metrics"
  ]
}
```

## 🔌 API Reference

### Endpoints

#### `POST /analyze`
Upload resume PDF and job description for analysis.

**Request:**
- `resume_file`: File (PDF)
- `job_description`: String (form data)

**Response:**
```json
{
  "success": true,
  "result": { /* AnalysisResult object */ },
  "processing_time_seconds": 45.2
}
```

#### `POST /analyze-text`
Analyze resume text (no PDF upload needed).

**Request Body:**
```json
{
  "resume_text": "string",
  "job_description": "string"
}
```

#### `GET /health`
Check API health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "openai",
  "embedding_provider": "openai",
  "api_configured": true
}
```

#### `GET /config`
Get current configuration (non-sensitive).

## 🧪 Testing

### Test with Sample Data

Use the provided sample job description:

```bash
# View sample job description
cat sample_data/sample_job_description.txt
```

Create a test resume PDF or use your own, then:
1. Start the app
2. Upload your resume
3. Paste the sample job description
4. Analyze

### API Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Analyze (with files)
curl -X POST http://localhost:8000/analyze \
  -F "resume_file=@path/to/resume.pdf" \
  -F "job_description=We are seeking a Senior Developer..."
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | REST API server |
| **Frontend** | Streamlit | Interactive web UI |
| **LLM** | OpenAI GPT-4 / Gemini | Natural language understanding |
| **Embeddings** | OpenAI / Sentence Transformers | Semantic similarity |
| **PDF Parsing** | pdfplumber, PyPDF2 | Extract text from PDFs |
| **Vector Ops** | scikit-learn, numpy | Cosine similarity |
| **Config** | Pydantic Settings | Environment management |

## 🎓 Key Concepts

### Prompt Engineering
The system uses carefully crafted prompts with:
- Clear system instructions
- Few-shot examples
- Structured JSON output requirements
- Domain-specific context (HR, recruiting)

### Semantic Matching
- Converts text to high-dimensional vectors (embeddings)
- Measures similarity using cosine distance
- Goes beyond keyword matching to understand context
- Example: "ML Engineer" matches "Machine Learning Specialist"

### ATS Optimization
- Analyzes keyword density
- Checks formatting compatibility
- Suggests improvements for parsing systems
- Recommends quantified achievements

## 🔒 Security & Privacy

- API keys stored in `.env` (never committed to git)
- Resume data not stored persistently
- All processing happens server-side
- CORS enabled for localhost only in production config
- No external data transmission (except to LLM APIs)

## 🐛 Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError`
```bash
# Ensure dependencies are installed
pip install -r requirements.txt
```

**Error:** `ValueError: OpenAI API key is required`
```bash
# Check your .env file
cat .env
# Ensure OPENAI_API_KEY is set correctly
```

### PDF Parsing Fails

**Error:** `Failed to extract text from PDF`
- Ensure PDF is not image-based (use OCR if needed)
- Check file is not corrupted
- Try re-saving the PDF

### Low Match Scores

- Ensure resume lists relevant skills explicitly
- Add years of experience clearly
- Use keywords from job description
- Quantify achievements with metrics

### Frontend Can't Connect to Backend

```bash
# Check backend is running
curl http://localhost:8000/health

# Check firewall/antivirus isn't blocking port 8000
```

## 📈 Future Enhancements

- [ ] Multi-job comparison (compare one resume against multiple jobs)
- [ ] Resume builder with templates
- [ ] Export analysis as PDF report
- [ ] Job market trend analysis
- [ ] Interview question generator based on gaps
- [ ] LinkedIn profile import
- [ ] Browser extension
- [ ] Batch processing for recruiters

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Google for Gemini API
- Streamlit team for the amazing framework
- FastAPI for the high-performance backend

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

---

**Built with ❤️ for job seekers everywhere**

*Last Updated: December 2025*
