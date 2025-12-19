# 🚀 Setup Guide - Resume Analyzer

This guide will walk you through setting up the Resume Analyzer from scratch.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] pip (Python package manager) installed
- [ ] An OpenAI API key OR Google Gemini API key
- [ ] Internet connection
- [ ] Terminal/Command Prompt access

### Check Your Python Version

```bash
python --version
# Should show: Python 3.10.x or higher
```

If you don't have Python 3.10+, download it from [python.org](https://www.python.org/downloads/).

## 🔑 Step 1: Get API Keys

### Option A: OpenAI (Recommended)

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

**Cost:** ~$0.02-0.10 per resume analysis (GPT-4)

### Option B: Google Gemini (Free Tier Available)

1. Go to [makersuite.google.com](https://makersuite.google.com/)
2. Sign in with Google account
3. Click "Get API Key"
4. Copy the API key

**Cost:** Free tier available, then pay-as-you-go

## 📦 Step 2: Install Dependencies

### Windows

```powershell
# Navigate to project directory
cd resume_analyser

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install packages
pip install -r requirements.txt
```

### Linux/Mac

```bash
# Navigate to project directory
cd resume_analyser

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

**Expected Installation Time:** 2-5 minutes

## ⚙️ Step 3: Configure Environment

### Create .env File

```bash
# Copy the example file
cp .env.example .env

# On Windows:
copy .env.example .env
```

### Edit .env File

Open `.env` in your text editor and configure:

#### For OpenAI:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

EMBEDDING_PROVIDER=openai
```

#### For Gemini:

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro

# For embeddings, use sentence-transformers (free, local)
EMBEDDING_PROVIDER=sentence-transformers
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

### Verify Configuration

```bash
# On Windows:
type .env

# On Linux/Mac:
cat .env
```

Ensure your API key is correctly set.

## 🧪 Step 4: Test Installation

### Test Backend

```bash
# Make sure venv is activated
python -m backend.main
```

You should see:
```
╔═══════════════════════════════════════════════╗
║     Resume Analyzer API Starting...          ║
╚═══════════════════════════════════════════════╝

🚀 Server: http://0.0.0.0:8000
📚 Docs: http://0.0.0.0:8000/docs
```

Press `Ctrl+C` to stop.

### Test Frontend (in new terminal)

```bash
# Activate venv again
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Run frontend
streamlit run frontend/app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Press `Ctrl+C` to stop.

## 🎯 Step 5: Run the Complete Application

### Automated Method (Recommended)

#### Windows (PowerShell):
```powershell
.\run.ps1
```

#### Linux/Mac:
```bash
chmod +x run.sh
./run.sh
```

This will:
1. Check and create .env if needed
2. Create/activate virtual environment
3. Install dependencies
4. Start both backend and frontend
5. Open browser automatically

### Manual Method

**Terminal 1 (Backend):**
```bash
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
python -m backend.main
```

**Terminal 2 (Frontend):**
```bash
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
streamlit run frontend/app.py
```

## 🎨 Step 6: Your First Analysis

1. **Open Browser**
   - Navigate to http://localhost:8501

2. **Prepare Resume**
   - Have your resume as a PDF
   - Maximum size: 10MB

3. **Prepare Job Description**
   - Copy a job posting from any job board
   - Include: requirements, skills, responsibilities
   - Use the sample in `sample_data/sample_job_description.txt` for testing

4. **Upload and Analyze**
   - Click "Upload Resume" and select your PDF
   - Paste job description in text area
   - Click "🚀 Analyze Resume"
   - Wait 30-60 seconds

5. **Review Results**
   - Match score and breakdown
   - Skills comparison
   - Improvement suggestions
   - Optimized bullets

## 🔧 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: "API key not configured"

**Solution:**
1. Check `.env` file exists
2. Verify API key is correct (no extra spaces)
3. Restart backend server

### Issue: Frontend shows "API Disconnected"

**Solution:**
1. Ensure backend is running: http://localhost:8000/health
2. Check firewall isn't blocking port 8000
3. Restart both servers

### Issue: PDF parsing fails

**Solution:**
1. Ensure PDF is text-based (not scanned image)
2. Try re-saving PDF
3. Check file isn't corrupted

### Issue: Slow analysis (>2 minutes)

**Possible causes:**
- First run (downloading models)
- Large resume/job description
- API rate limiting

**Solution:**
- Wait for first run to complete
- Try with shorter text
- Check API quota/limits

### Issue: Import errors with sentence-transformers

**Solution:**
```bash
pip install sentence-transformers torch --upgrade
```

### Issue: Permission denied on run.sh

**Solution:**
```bash
chmod +x run.sh
```

## 💡 Usage Tips

### For Best Results:

1. **Resume Quality**
   - Use PDF format (not Word or images)
   - Include clear section headers
   - List skills explicitly
   - Quantify achievements

2. **Job Description**
   - Include complete job posting
   - Paste "Requirements" and "Qualifications" sections
   - Include skill lists

3. **Multiple Iterations**
   - Run analysis
   - Apply suggestions
   - Re-analyze to see improvement

### Sample Resume Format:

```
JOHN DOE
john.doe@email.com | LinkedIn | GitHub

EXPERIENCE
Senior Software Engineer | Company | 2020-Present
• Built scalable APIs serving 1M+ users using Python and FastAPI
• Reduced latency by 40% through database optimization
• Mentored team of 5 junior engineers

SKILLS
Languages: Python, JavaScript, SQL
Frameworks: FastAPI, Django, React
Tools: Docker, Kubernetes, AWS, PostgreSQL

EDUCATION
BS Computer Science | University | 2018
```

## 📊 Understanding the Results

### Match Score Ranges:

- **75-100**: Strong Match → Apply with confidence
- **50-74**: Moderate Match → Address gaps, then apply
- **0-49**: Weak Match → Major skill gaps, consider upskilling

### Priority Levels:

- **High**: Critical for this role, implement immediately
- **Medium**: Important, implement if possible
- **Low**: Nice to have, consider for polish

## 🔄 Updating the Project

```bash
# Pull latest changes (if from git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart servers
```

## 🛑 Stopping the Application

### If using run.ps1 (Windows):
```powershell
# Check running jobs
Get-Job

# Stop specific job
Stop-Job -Id <JobId>

# Or stop all
Get-Job | Stop-Job
```

### If using run.sh or manual:
- Press `Ctrl+C` in each terminal

## 📚 Next Steps

1. ✅ Complete first analysis
2. 📖 Read the full README.md
3. 🎯 Test with different resumes
4. 💡 Apply improvement suggestions
5. 🔄 Re-analyze and compare scores
6. 🌟 Star the project if helpful!

## 🆘 Getting Help

1. **Check README.md** - Comprehensive documentation
2. **Review Troubleshooting** - Common issues and fixes
3. **Check Backend Logs** - Error messages in terminal
4. **API Documentation** - http://localhost:8000/docs
5. **Test API Health** - http://localhost:8000/health

## ✅ Setup Complete!

You're now ready to analyze resumes! 🎉

**Quick Commands Reference:**

```bash
# Start everything (automated)
.\run.ps1           # Windows
./run.sh            # Linux/Mac

# Start manually
python -m backend.main          # Backend
streamlit run frontend/app.py   # Frontend

# Test
curl http://localhost:8000/health  # Check API
```

---

**Happy Analyzing! 📄✨**
