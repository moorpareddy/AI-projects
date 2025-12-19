"""
Configuration module for Resume Analyzer
Loads environment variables and provides centralized config access
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # LLM Configuration
    llm_provider: Literal["openai", "gemini", "local"] = Field(default="openai")
    
    # OpenAI Settings
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4-turbo-preview")
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    
    # Gemini Settings
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-pro")
    
    # Local Model Settings
    local_model_path: str = Field(default="")
    
    # Embedding Configuration
    embedding_provider: Literal["openai", "sentence-transformers"] = Field(default="openai")
    sentence_transformer_model: str = Field(default="all-MiniLM-L6-v2")
    
    # Application Settings
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    frontend_port: int = Field(default=8501)
    
    # Scoring Weights
    weight_skills_match: float = Field(default=0.40)
    weight_experience_relevance: float = Field(default=0.30)
    weight_semantic_similarity: float = Field(default=0.20)
    weight_resume_quality: float = Field(default=0.10)
    
    # API Settings
    max_resume_size_mb: int = Field(default=10)
    allowed_file_types: str = Field(default="pdf")
    request_timeout_seconds: int = Field(default=60)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def validate_api_keys(self) -> bool:
        """Validate that required API keys are present based on provider"""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("Gemini API key is required when using Gemini provider")
        if self.embedding_provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI embeddings")
        return True
    
    def get_weights_dict(self) -> dict[str, float]:
        """Return scoring weights as dictionary"""
        return {
            "skills_match": self.weight_skills_match,
            "experience_relevance": self.weight_experience_relevance,
            "semantic_similarity": self.weight_semantic_similarity,
            "resume_quality": self.weight_resume_quality
        }


# Global settings instance
settings = Settings()

# Validate settings on module import
try:
    settings.validate_api_keys()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
    print("Please set up your .env file with the required API keys")
