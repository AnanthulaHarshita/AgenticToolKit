import openai
from app.services.embedding_store import search_embeddings

def extract_suggested_query(answer):
    # Simple extraction logic; improve as needed
    import re
    match = re.search(r"suggested query:\s*(.*)", answer, re.IGNORECASE)
    return match.group(1).strip() if match else None

def agentic_rag(query):
    results = search_embeddings(query, top_k=3)
    context = "\n---\n".join([open(r["file"], encoding="utf-8").read() for r in results])

    prompt = f"""You are an expert assistant. Here is the context:
{context}

User question: {query}

If the context is enough to answer, answer the question. If not, suggest a new search query to get more info.
Answer or suggest a new query:"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content

    if "suggested query:" in answer.lower():
        new_query = extract_suggested_query(answer)
        new_results = search_embeddings(new_query, top_k=3)
        new_context = "\n---\n".join([open(r["file"], encoding="utf-8").read() for r in new_results])
        prompt2 = f"""Here is more context:
{new_context}

Original question: {query}
Now answer the question:"""
        response2 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt2}]
        )
        final_answer = response2.choices[0].message.content
        return final_answer
    else:
        return answer