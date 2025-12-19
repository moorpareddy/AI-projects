"""
Job Description Parser - Extracts structured information from job postings
Uses LLM to intelligently parse requirements and qualifications
"""
import re
import json
from typing import Optional

from .config import settings
from .schemas import JobDescriptionData
from .prompts import SYSTEM_PROMPT, JOB_DESCRIPTION_EXTRACTION_PROMPT, format_prompt


class JobParser:
    """Parse and extract structured information from job descriptions"""
    
    def __init__(self):
        self.llm_provider = settings.llm_provider
    
    def parse_job_description(self, job_text: str) -> JobDescriptionData:
        """
        Parse job description and extract structured information
        
        Args:
            job_text: Raw job description text
            
        Returns:
            JobDescriptionData object with extracted requirements
        """
        # Clean the text
        job_text = self._clean_text(job_text)
        
        if not job_text or len(job_text.strip()) < 20:
            raise ValueError("Job description is too short or empty")
        
        # Use LLM to extract structured data
        structured_data = self._extract_structured_data(job_text)
        
        # Create JobDescriptionData object
        job_data = JobDescriptionData(
            raw_text=job_text,
            required_skills=structured_data.get("required_skills", []),
            preferred_skills=structured_data.get("preferred_skills", []),
            responsibilities=structured_data.get("responsibilities", []),
            required_experience_years=structured_data.get("required_experience_years"),
            qualifications=structured_data.get("qualifications", [])
        )
        
        return job_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize job description text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove special characters
        text = text.replace('\x00', '')
        
        return text.strip()
    
    def _extract_structured_data(self, job_text: str) -> dict:
        """
        Use LLM to extract structured information from job description
        
        Args:
            job_text: Raw job description text
            
        Returns:
            Dictionary with extracted fields
        """
        prompt = format_prompt(JOB_DESCRIPTION_EXTRACTION_PROMPT, job_description=job_text)
        
        response = ""
        try:
            response = self._call_llm(prompt)
            print(f"\n=== Job LLM Response (first 300 chars) ===")
            print(response[:300])
            print(f"=== End Response ===")
            
            # Remove markdown code blocks if present
            cleaned = response.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
            cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r'```$', '', cleaned)
            cleaned = cleaned.strip()
            
            # Parse JSON from response
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return data
            else:
                return json.loads(cleaned)
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error in job parser: {e}")
            print(f"Full response: {response}")
            # Fallback to basic extraction
            return self._fallback_extraction(job_text)
        except Exception as e:
            print(f"Error extracting structured data from job description: {e}")
            print(f"Full response: {response}")
            import traceback
            traceback.print_exc()
            # Fallback to basic extraction
            return self._fallback_extraction(job_text)
    
    def _fallback_extraction(self, job_text: str) -> dict:
        """
        Fallback extraction using pattern matching if LLM fails
        
        Args:
            job_text: Raw job description text
            
        Returns:
            Dictionary with basic extracted fields
        """
        text_lower = job_text.lower()
        
        # Extract skills (basic keyword matching)
        tech_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'Machine Learning', 'TensorFlow', 'PyTorch', 'REST API', 'GraphQL'
        ]
        
        required_skills = []
        preferred_skills = []
        
        # Try to identify sections
        required_section = ""
        preferred_section = ""
        
        # Look for "required" vs "preferred" sections
        if "required:" in text_lower or "requirements:" in text_lower:
            parts = re.split(r'(?i)(required|requirements|preferred|nice to have|bonus):', job_text)
            for i, part in enumerate(parts):
                if i > 0 and parts[i-1].lower() in ['required', 'requirements']:
                    required_section = part[:500]  # Take first 500 chars
                elif i > 0 and parts[i-1].lower() in ['preferred', 'nice to have', 'bonus']:
                    preferred_section = part[:500]
        
        # Extract skills from respective sections
        for keyword in tech_keywords:
            if required_section and keyword.lower() in required_section.lower():
                required_skills.append(keyword)
            elif preferred_section and keyword.lower() in preferred_section.lower():
                preferred_skills.append(keyword)
            elif keyword.lower() in text_lower:
                # If no clear sections, put in required by default
                required_skills.append(keyword)
        
        # Extract years of experience
        experience_years = None
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(?:of\s*)?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*required'
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                experience_years = float(match.group(1))
                break
        
        return {
            "required_skills": list(set(required_skills)),  # Remove duplicates
            "preferred_skills": list(set(preferred_skills)),
            "responsibilities": [],
            "required_experience_years": experience_years,
            "qualifications": []
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
