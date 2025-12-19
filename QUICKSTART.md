# 🚀 QUICK START - Resume Analyzer

**Get started in 5 minutes!**

## ⚡ Super Quick Setup

### 1. Get an API Key (2 minutes)
- **OpenAI**: https://platform.openai.com/api-keys
- **OR Gemini**: https://makersuite.google.com/app/apikey

### 2. Configure (1 minute)
```bash
# Copy and edit .env file
copy .env.example .env

# Edit .env and add your API key:
# For OpenAI:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# For Gemini:
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
```

### 3. Run (2 minutes)
```powershell
# Windows - Run this command:
.\run.ps1

# Linux/Mac - Run this command:
chmod +x run.sh && ./run.sh
```

### 4. Use!
1. Open http://localhost:8501 in browser
2. Upload your resume PDF
3. Paste a job description
4. Click "Analyze Resume"
5. Get instant feedback!

---

## 📦 Manual Setup (If run script doesn't work)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start backend (Terminal 1)
python -m backend.main

# 5. Start frontend (Terminal 2)
streamlit run frontend/app.py

# 6. Open browser to http://localhost:8501
```

---

## 🎯 Usage

### Basic Flow:
```
Upload PDF → Paste Job → Click Analyze → Get Results
```

### What You Get:
- ✅ Match score (0-100)
- 📊 Score breakdown
- 🔍 Skills analysis
- 💡 Improvement tips
- ✨ Optimized bullets
- 🎓 Final verdict

---

## ⚙️ Configuration Options

Edit `.env` file:

```bash
# Choose your AI provider
LLM_PROVIDER=openai          # or gemini

# Add your API key
OPENAI_API_KEY=sk-...        # Your key here
# OR
GEMINI_API_KEY=...           # Your key here

# Adjust scoring weights (optional)
WEIGHT_SKILLS_MATCH=0.40
WEIGHT_EXPERIENCE_RELEVANCE=0.30
WEIGHT_SEMANTIC_SIMILARITY=0.20
WEIGHT_RESUME_QUALITY=0.10
```

---

## 🔧 Troubleshooting

### Problem: "API key not configured"
**Fix:** Check your `.env` file has the correct API key

### Problem: "Frontend shows API Disconnected"
**Fix:** Make sure backend is running: `python -m backend.main`

### Problem: "Module not found"
**Fix:** Install dependencies: `pip install -r requirements.txt`

### Problem: PDF won't parse
**Fix:** Ensure PDF is text-based (not a scanned image)

---

## 📚 Full Documentation

- **Complete Guide:** [README.md](README.md)
- **Setup Details:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Project Overview:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🆘 Quick Help

### Check if everything is running:
```bash
# Backend health
curl http://localhost:8000/health

# Open frontend
http://localhost:8501
```

### Restart everything:
```bash
# Stop with Ctrl+C, then:
.\run.ps1  # Windows
./run.sh   # Linux/Mac
```

---

## 🎉 First Analysis Tips

1. **Use a real job posting** - Copy from LinkedIn, Indeed, etc.
2. **Include full requirements** - Skills, experience, responsibilities
3. **Wait 30-60 seconds** - AI processing takes time
4. **Apply suggestions** - Use the improvement tips
5. **Re-analyze** - See how your score improves!

---

## 💰 Cost Estimate

**Per resume analysis:**
- OpenAI (GPT-4): ~$0.02-0.10
- Gemini: Free tier available

**100 resumes ≈ $2-10 (OpenAI)**

---

## ✅ Quick Checklist

Before analyzing:
- [ ] Backend running (check http://localhost:8000/health)
- [ ] Frontend open (http://localhost:8501)
- [ ] Resume is PDF format
- [ ] Job description copied
- [ ] API key configured in .env

---

**You're all set! Start analyzing resumes now! 🚀**

Need more help? See [SETUP_GUIDE.md](SETUP_GUIDE.md)
