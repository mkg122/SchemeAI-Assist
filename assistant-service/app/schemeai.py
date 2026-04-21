import config
import google.generativeai as genai
from vector_search import search_schemes

genai.configure(api_key=config.GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def ask_scheme_ai(user_question: str) -> str:
    
    retrieved_context = search_schemes(user_question, top_k=3)
    
    if not retrieved_context.strip():
        return "I'm sorry, I couldn't find any relevant scheme information."

    prompt = f"""
    <role>
    You are SchemeAI Assistant, a AI assistant specializing in Indian Government Schemes.
    </role>
    
    <instructions>
    - You must answer the User's Question using ONLY the information provided in the Context below.
    - If the answer is not contained within the Context, you must explicitly state: "I don't have enough information on that based on the provided schemes."
    - Do NOT use any outside knowledge.
    - Format your answer clearly, using bullet points if necessary.
    </instructions>
    
    <context>
    {retrieved_context}
    </context>
    
    <task>
    {user_question}
    </task>
    
    Answer:
    """
    
    response = model.generate_content(prompt)
    
    return response.text