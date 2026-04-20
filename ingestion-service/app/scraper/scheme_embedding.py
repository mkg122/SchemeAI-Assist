import config 
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def get_pinecone_index():
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    return pc.Index(config.PINECONE_INDEX_NAME)

def process_and_embed(shemes: list):
    index = get_pinecone_index()
    scheme_vectors = []
    
    print("Processing data for vector embedding...")
    
    for scheme in shemes:
        scheme_name = scheme.get("scheme_name", "Unknown Scheme")
        ministry = scheme.get("ministry", "Unknown Ministry")
        
        sections_to_embed = ["details", "benefits", "eligibility", "application_process", "documents_required"]
        
        for section in sections_to_embed:
            content = scheme.get(section)
            if not content:
                continue
                
            clean_content = content.replace('\ufeff', '').strip()
            rich_text = f"Scheme Name: {scheme_name}\nMinistry: {ministry}\nSection: {section.title().replace('_', ' ')}\nContent: {clean_content}"
            chunk_id = f"{scheme_name.replace(' ', '_')}_{section}"
            
            embedding = embedder.encode(rich_text).tolist()
            
            metadata = {
                "scheme_name": scheme_name,
                "ministry": ministry,
                "section": section,
                "text": rich_text
            }
            
            scheme_vectors.append((chunk_id, embedding, metadata))

    batch_size = 100
    if scheme_vectors:
        print("Embedding of chunks to Pinecone started.")
        
        for i in range(0, len(scheme_vectors), batch_size):
            batch = scheme_vectors[i : i + batch_size]
            index.upsert(vectors=batch)
    else:
        print("Empty vectors list.")