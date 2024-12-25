# YouTube_Summarizer

High-Level Architecture
Data Ingestion and Preprocessing:

Preprocess Metadata: 
- Parse metadata like title, description, tags, views, etc., from YouTube.
- Extract and Chunk Transcripts: Divide long transcripts into manageable chunks while maintaining semantic coherence.
- Vectorize Metadata and Transcripts: Use embeddings (e.g., via a transformer like sentence-transformers) to generate dense vectors.

Indexing:
- Store embeddings and metadata in a vector database (e.g., Pinecone, Weaviate, FAISS) for efficient retrieval.

RAG Pipeline:
- Retrieval: Retrieve relevant chunks of transcripts or metadata based on user queries using cosine similarity in the vector database.
- Augmentation: Combine the retrieved context with user queries to form an augmented prompt.
- Generation: Use LLaMA 3.2 (via replicate) to generate responses based on the augmented prompt.

Conversational Loop:
- Maintain dialogue history for contextual responses across turns.