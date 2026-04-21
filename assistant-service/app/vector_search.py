import config
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def get_pinecone_index():
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    return pc.Index(config.PINECONE_INDEX_NAME)

def search_schemes(user_question: str, top_k: int = 3) -> str:
    index = get_pinecone_index()
    
    question_embedding = embedder.encode(user_question).tolist()
    
    results = index.query(
        vector=question_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    context_chunks = []
    if results and 'matches' in results:
        for match in results['matches']:
            if match['score'] > 0.3:
                context_chunks.append(match['metadata']['text'])
                
    final_context = "\n\n---\n\n".join(context_chunks)
    return final_context
