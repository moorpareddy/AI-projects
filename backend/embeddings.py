"""
Embeddings Module - Handles text embedding generation and similarity computation
Supports OpenAI embeddings and local sentence-transformers
"""
import numpy as np
from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity

from .config import settings


class EmbeddingService:
    """Generate embeddings and compute semantic similarity"""
    
    def __init__(self):
        self.provider = settings.embedding_provider
        self.model = None
        
        # Initialize the embedding model based on provider
        if self.provider == "sentence-transformers":
            try:
                self._init_sentence_transformer()
            except Exception as e:
                print(f"Warning: Could not initialize sentence-transformers: {e}")
                print("Embeddings will return basic scores. Install fully for semantic matching.")
                self.model = None
    
    def _init_sentence_transformer(self):
        """Initialize sentence-transformers model"""
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(settings.sentence_transformer_model)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if self.provider == "openai":
            return self._get_openai_embedding(text)
        elif self.provider == "sentence-transformers":
            if self.model is None:
                # Return dummy embedding if model not loaded
                return [0.0] * 384
            return self._get_sentence_transformer_embedding(text)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.provider == "openai":
            return [self._get_openai_embedding(text) for text in texts]
        elif self.provider == "sentence-transformers":
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1, where 1 is most similar)
        """
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        
        # Compute cosine similarity
        similarity = cosine_similarity(
            [embedding1],
            [embedding2]
        )[0][0]
        
        # Convert to 0-100 scale
        return float(similarity)
    
    def compute_similarity_matrix(
        self, 
        texts1: List[str], 
        texts2: List[str]
    ) -> np.ndarray:
        """
        Compute pairwise similarity matrix between two sets of texts
        
        Args:
            texts1: First set of texts
            texts2: Second set of texts
            
        Returns:
            Matrix of similarity scores
        """
        embeddings1 = self.get_embeddings_batch(texts1)
        embeddings2 = self.get_embeddings_batch(texts2)
        
        return cosine_similarity(embeddings1, embeddings2)
    
    def find_most_similar(
        self, 
        query: str, 
        candidates: List[str], 
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar candidates to a query
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top matches to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        query_embedding = self.get_embedding(query)
        candidate_embeddings = self.get_embeddings_batch(candidates)
        
        similarities = cosine_similarity(
            [query_embedding],
            candidate_embeddings
        )[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI API"""
        import openai
        
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text
        )
        
        return response.data[0].embedding
    
    def _get_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Get embedding from sentence-transformers"""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()


class SemanticMatcher:
    """High-level semantic matching functionality"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    def match_resume_to_job(self, resume_text: str, job_text: str) -> dict:
        """
        Compute semantic match between resume and job description
        
        Args:
            resume_text: Full resume text
            job_text: Full job description text
            
        Returns:
            Dictionary with similarity metrics
        """
        # Overall similarity
        overall_similarity = self.embedding_service.compute_similarity(
            resume_text, 
            job_text
        )
        
        return {
            "overall_similarity": overall_similarity,
            "semantic_match_score": overall_similarity * 100  # Scale to 0-100
        }
    
    def match_skills(
        self, 
        resume_skills: List[str], 
        required_skills: List[str]
    ) -> dict:
        """
        Match resume skills against required skills using semantic similarity
        
        Args:
            resume_skills: List of skills from resume
            required_skills: List of required skills from job
            
        Returns:
            Dictionary with matching information
        """
        if not resume_skills or not required_skills:
            return {
                "matched_pairs": [],
                "unmatched_required": required_skills,
                "match_rate": 0.0
            }
        
        # Compute similarity matrix
        similarity_matrix = self.embedding_service.compute_similarity_matrix(
            resume_skills, 
            required_skills
        )
        
        # Find best matches for each required skill
        matched_pairs = []
        unmatched_required = []
        
        threshold = 0.7  # Similarity threshold for considering a match
        
        for j, req_skill in enumerate(required_skills):
            # Find best matching resume skill
            similarities = similarity_matrix[:, j]
            best_idx = int(np.argmax(similarities))
            best_score = float(similarities[best_idx])
            
            if best_score >= threshold:
                matched_pairs.append({
                    "resume_skill": resume_skills[best_idx],
                    "required_skill": req_skill,
                    "similarity": best_score
                })
            else:
                unmatched_required.append(req_skill)
        
        match_rate = len(matched_pairs) / len(required_skills) if required_skills else 0
        
        return {
            "matched_pairs": matched_pairs,
            "unmatched_required": unmatched_required,
            "match_rate": match_rate
        }
    
    def compute_section_similarities(
        self, 
        resume_sections: dict, 
        job_sections: dict
    ) -> dict:
        """
        Compute similarities between corresponding sections
        
        Args:
            resume_sections: Dictionary of resume sections (e.g., experience, skills)
            job_sections: Dictionary of job sections (e.g., responsibilities, requirements)
            
        Returns:
            Dictionary with section-wise similarities
        """
        similarities = {}
        
        for section_name in job_sections:
            if section_name in resume_sections:
                resume_text = " ".join(resume_sections[section_name]) if isinstance(resume_sections[section_name], list) else resume_sections[section_name]
                job_text = " ".join(job_sections[section_name]) if isinstance(job_sections[section_name], list) else job_sections[section_name]
                
                if resume_text and job_text:
                    similarity = self.embedding_service.compute_similarity(
                        resume_text, 
                        job_text
                    )
                    similarities[section_name] = similarity * 100
        
        return similarities
