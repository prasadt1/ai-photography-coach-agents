"""
FAISS Vector Store for Photography Knowledge Base

This module handles PDF ingestion and similarity search using FAISS.
Provides broader knowledge coverage as secondary source to curated entries.

Architecture:
- Primary: Curated knowledge (20 entries, high quality, cited)
- Secondary: FAISS PDF search (broader coverage, context retrieval)

Author: AI Photography Coach
"""

import os
from typing import List, Dict, Optional
from pathlib import Path

# Lazy imports to avoid loading unless needed
def _lazy_imports():
    """Import heavy dependencies only when actually using FAISS"""
    global RecursiveCharacterTextSplitter, PyPDFLoader, HuggingFaceEmbeddings, FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS


class FAISSKnowledgeStore:
    """
    Manages FAISS vector store for photography PDFs.
    
    Handles:
    - PDF ingestion and chunking
    - Embedding generation (all-MiniLM-L6-v2)
    - Persistent storage (faiss_index/)
    - Similarity search with metadata
    """
    
    def __init__(
        self, 
        data_path: str = "agents_capstone/data/pdfs",
        index_path: str = "agents_capstone/data/faiss_index"
    ):
        """
        Initialize FAISS store.
        
        Args:
            data_path: Directory containing PDF files
            index_path: Directory to save/load FAISS index
        """
        self.data_path = Path(data_path)
        self.index_path = Path(index_path)
        self.db = None
        self.embeddings = None
        
        # Load existing index if available
        if self.index_path.exists():
            self.load_index()
    
    def load_index(self):
        """Load existing FAISS index from disk"""
        if not self.index_path.exists():
            print(f"⚠️  No index found at {self.index_path}")
            return False
        
        try:
            _lazy_imports()
            print(f"📂 Loading FAISS index from {self.index_path}...")
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.db = FAISS.load_local(
                str(self.index_path), 
                self.embeddings,
                allow_dangerous_deserialization=True  # Local files only, safe
            )
            print(f"✅ Loaded FAISS index with {self.db.index.ntotal} vectors")
            return True
        except Exception as e:
            print(f"❌ Failed to load index: {e}")
            return False
    
    def ingest_pdfs(self, progress_callback=None) -> bool:
        """
        Ingest all PDFs from data_path and create FAISS index.
        
        Args:
            progress_callback: Optional function(step, total, message) for UI updates
        
        Returns:
            True if successful, False otherwise
        """
        _lazy_imports()
        
        # Find all PDF files
        pdf_files = list(self.data_path.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in {self.data_path}")
            return False
        
        print(f"📚 Found {len(pdf_files)} PDF files")
        if progress_callback:
            progress_callback(0, len(pdf_files) + 2, "Loading PDFs...")
        
        # Load all PDFs
        documents = []
        for idx, pdf_file in enumerate(pdf_files, 1):
            try:
                print(f"  📄 Loading {pdf_file.name}...")
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                
                # Add metadata
                for doc in docs:
                    doc.metadata['source_file'] = pdf_file.name
                    doc.metadata['source_type'] = 'pdf'
                
                documents.extend(docs)
                
                if progress_callback:
                    progress_callback(idx, len(pdf_files) + 2, f"Loaded {pdf_file.name}")
            except Exception as e:
                print(f"  ⚠️  Failed to load {pdf_file.name}: {e}")
        
        if not documents:
            print("❌ No documents loaded successfully")
            return False
        
        print(f"✅ Loaded {len(documents)} pages from {len(pdf_files)} PDFs")
        
        # Split into chunks
        if progress_callback:
            progress_callback(len(pdf_files) + 1, len(pdf_files) + 2, "Splitting documents...")
        
        print("✂️  Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Create embeddings and FAISS index
        if progress_callback:
            progress_callback(len(pdf_files) + 2, len(pdf_files) + 2, "Creating embeddings (2-3 min)...")
        
        print("🧠 Creating embeddings (this takes 2-3 minutes)...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db = FAISS.from_documents(chunks, self.embeddings)
        
        # Save index to disk
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.db.save_local(str(self.index_path))
        print(f"✅ Vector store created and saved to {self.index_path}")
        
        return True
    
    def search(
        self, 
        query: str, 
        k: int = 3,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Semantic search for relevant photography knowledge.
        
        Args:
            query: User question or topic
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1). None = return all
        
        Returns:
            List of dicts with 'text', 'source', 'score'
        """
        if self.db is None:
            print("⚠️  FAISS index not loaded. Call load_index() first.")
            return []
        
        try:
            # Similarity search with scores
            results = self.db.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                # Convert distance to similarity (lower distance = higher similarity)
                similarity = 1 / (1 + score)
                
                # Filter by threshold if provided
                if score_threshold and similarity < score_threshold:
                    continue
                
                formatted_results.append({
                    'text': doc.page_content,
                    'source': doc.metadata.get('source_file', 'Unknown'),
                    'score': round(similarity, 3),
                    'metadata': doc.metadata
                })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        if self.db is None:
            return {
                'status': 'not_loaded',
                'total_vectors': 0,
                'index_exists': self.index_path.exists()
            }
        
        return {
            'status': 'loaded',
            'total_vectors': self.db.index.ntotal,
            'index_path': str(self.index_path),
            'index_size_mb': self._get_index_size(),
        }
    
    def _get_index_size(self) -> float:
        """Calculate total size of index files in MB"""
        if not self.index_path.exists():
            return 0.0
        
        total_size = 0
        for file_path in self.index_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return round(total_size / (1024 * 1024), 2)


# Global instance for singleton pattern
_faiss_store = None

def get_faiss_store() -> FAISSKnowledgeStore:
    """Get or create global FAISS store instance"""
    global _faiss_store
    if _faiss_store is None:
        _faiss_store = FAISSKnowledgeStore()
    return _faiss_store


if __name__ == "__main__":
    # Quick test
    store = FAISSKnowledgeStore()
    
    # Check if index exists
    stats = store.get_stats()
    print(f"\n📊 FAISS Store Stats:")
    print(f"   Status: {stats['status']}")
    print(f"   Vectors: {stats['total_vectors']}")
    
    if stats['status'] == 'not_loaded':
        print("\n🔧 To create index, run:")
        print("   python3 -m agents_capstone.admin_ui")
        print("   Or use: store.ingest_pdfs()")
    else:
        # Test search
        print("\n🔍 Testing search...")
        results = store.search("rule of thirds composition", k=2)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['score']}")
            print(f"   Source: {result['source']}")
            print(f"   Text: {result['text'][:100]}...")
