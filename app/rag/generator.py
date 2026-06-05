import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def generate_answer(question: str, chunks: list[dict]) -> dict:
    citations = [
        {"index": i + 1, "source": c.get("source", ""), "page": c.get("page", "")}
        for i, c in enumerate(chunks)
    ]

    client = _get_client()
    if client is None:
        return {
            "answer": "Answer generation is unavailable because GROQ_API_KEY is not configured.",
            "citations": citations,
        }

    # Build context string with citations labeled
    context = ""
    for i, chunk in enumerate(chunks):
        context += (
            f"\n[{i + 1}] Source: {chunk.get('source', '')}, "
            f"Page {chunk.get('page', '')}\n{chunk.get('text', '')}\n"
        )

    prompt = f"""You are a helpful college admin assistant.
Answer the student's question using ONLY the context provided below.
After every fact you state, add a citation like [1], [2] matching the source number.
If the answer is not in the context, say: "I could not find this information in the college documents."

Context:
{context}

Student Question: {question}

Answer:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
    except Exception:
        return {
            "answer": "Answer generation is temporarily unavailable. Please try again later.",
            "citations": citations,
        }

    answer_text = response.choices[0].message.content

    return {"answer": answer_text, "citations": citations}
