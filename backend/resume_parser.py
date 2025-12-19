"""
Resume Parser - Extracts structured information from PDF resumes
Uses pdfplumber for PDF extraction and LLM for intelligent parsing
"""
import re
import json
from typing import Optional
import pdfplumber
from PyPDF2 import PdfReader
import io

from .config import settings
from .schemas import ResumeData
from .prompts import SYSTEM_PROMPT, RESUME_EXTRACTION_PROMPT, format_prompt


class ResumeParser:
    """Parse and extract structured information from resume PDFs"""
    
    def __init__(self):
        self.llm_provider = settings.llm_provider
        
    def extract_text_from_pdf(self, pdf_file: bytes) -> str:
        """
        Extract raw text from PDF file
        
        Args:
            pdf_file: PDF file as bytes
            
        Returns:
            Extracted text content
        """
        text = ""
        
        try:
            # Try with pdfplumber first (better formatting preservation)
            with pdfplumber.open(io.BytesIO(pdf_file)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            try:
                pdf_reader = PdfReader(io.BytesIO(pdf_file))
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
            except Exception as e2:
                raise ValueError(f"Failed to extract text from PDF: {e2}")
        
        # Clean up the text
        text = self._clean_text(text)
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Extracted text is too short or empty. Please check the PDF file.")
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove special characters that might interfere
        text = text.replace('\x00', '')
        
        return text.strip()
    
    def parse_resume(self, pdf_file: bytes) -> ResumeData:
        """
        Parse resume PDF and extract structured information
        
        Args:
            pdf_file: Resume PDF as bytes
            
        Returns:
            ResumeData object with extracted information
        """
        # Extract raw text
        raw_text = self.extract_text_from_pdf(pdf_file)
        
        # Use LLM to extract structured data
        structured_data = self._extract_structured_data(raw_text)
        
        # Create ResumeData object
        resume_data = ResumeData(
            raw_text=raw_text,
            skills=structured_data.get("skills", []),
            experience_years=structured_data.get("experience_years"),
            education=structured_data.get("education", []),
            projects=structured_data.get("projects", []),
            certifications=structured_data.get("certifications", []),
            work_experience=structured_data.get("work_experience", [])
        )
        
        return resume_data
    
    def _extract_structured_data(self, resume_text: str) -> dict:
        """
        Use LLM to extract structured information from resume text
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Dictionary with extracted fields
        """
        prompt = format_prompt(RESUME_EXTRACTION_PROMPT, resume_text=resume_text)
        
        response = ""
        try:
            response = self._call_llm(prompt)
            print(f"\n=== LLM Response (first 300 chars) ===")
            print(response[:300])
            print(f"=== End Response ===")
            
            # Remove markdown code blocks if present
            cleaned = response.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
            cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r'```$', '', cleaned)
            cleaned = cleaned.strip()
            
            # Parse JSON from response
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return data
            else:
                # Try parsing the entire cleaned response as JSON
                return json.loads(cleaned)
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Full response: {response}")
            # Return basic structure with fallback parsing
            return self._fallback_extraction(resume_text)
        except Exception as e:
            print(f"Error extracting structured data: {e}")
            print(f"Full response: {response}")
            import traceback
            traceback.print_exc()
            # Return basic structure with fallback parsing
            return self._fallback_extraction(resume_text)
    
    def _fallback_extraction(self, resume_text: str) -> dict:
        """
        Fallback extraction using regex patterns if LLM fails
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Dictionary with basic extracted fields
        """
        # Basic skill extraction (common tech keywords)
        tech_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'scikit-learn',
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum'
        ]
        
        skills = []
        text_lower = resume_text.lower()
        for keyword in tech_keywords:
            if keyword.lower() in text_lower:
                skills.append(keyword)
        
        # Try to extract years of experience
        experience_years = None
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:\s*(\d+)\+?\s*years?'
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                experience_years = float(match.group(1))
                break
        
        return {
            "skills": skills,
            "experience_years": experience_years,
            "education": [],
            "projects": [],
            "certifications": [],
            "work_experience": []
        }
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the configured LLM provider
        
        Args:
            prompt: The prompt to send
            
        Returns:
            LLM response text
        """
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
            max_tokens=2000
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
