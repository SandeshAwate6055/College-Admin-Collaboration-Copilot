import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Minimum relevance score — chunks below this are considered "not found"
MIN_RELEVANCE_SCORE = 0.25


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


SYSTEM_PROMPT = """You are the official AI Academic Advisor for Vishwakarma Institute of Technology (VIT), Pune (Autonomous Institute, NAAC A++ Grade, affiliated to SPPU).

Your role is to guide students, parents, and faculty by answering questions based strictly on the official VIT Pune documents provided.

STRUCTURE YOUR ANSWERS IN THIS FORMAT:
1. 📌 Overview: Begin with a warm, polite 1-2 sentence direct summary answering the query.
2. 📋 Official Details & Rules: Present the core details, course structures, formulas, criteria, or procedures clearly using organized bullet points, bold key terms, or clean Markdown tables.
3. 💡 Student Guidance & Next Steps: Highlight practical tips (such as prerequisites, deadlines, credit limits, or where to submit forms).
4. 📄 Official References: Naturally mention the source document name(s) and page number(s) (e.g. *(Source: SGPA_CGPA_Calculation.pdf, Page 1)*).

TONE & STYLE GUIDELINES:
- Warm, empathetic, professional, and student-friendly. Never be blunt, cold, or overly robotic.
- Bold important numbers, deadlines, formulas, course codes, and criteria for easy readability.
- If the official excerpts only partially cover the question, clearly explain what is covered from the documents, and politely guide the student on how to check further details via www.vit.edu or the Student Section / HoD office.
- Never invent facts, course names, or rules not present in the excerpts.
"""


def _chunks_are_relevant(chunks: list[dict]) -> bool:
    """Check if at least one chunk was retrieved."""
    return bool(chunks)


def generate_answer(question: str, chunks: list[dict]) -> dict:
    citations = [
        {"index": i + 1, "source": c.get("source", ""), "page": c.get("page", "")}
        for i, c in enumerate(chunks)
    ]

    client = _get_client()
    if client is None:
        return {
            "answer": (
                "Answer generation is currently unavailable because GROQ_API_KEY is not configured.\n\n"
                "Please visit **www.vit.edu** or contact the VIT Student Section directly."
            ),
            "citations": citations,
        }

    # If no chunks found, return honest "not found" message
    if not chunks:
        return {
            "answer": (
                "Hello! I searched the official VIT Pune knowledge base, but couldn't find specific documentation covering this topic.\n\n"
                "**Here are the best ways to get this information:**\n"
                "- 🌐 Visit the official portal: **[www.vit.edu](https://www.vit.edu)**\n"
                "- 🏫 Visit the **Student Section** or respective **Department HoD Office** at Bibwewadi Campus\n"
                "- 🎫 Submit an official query ticket via the **Grievance Desk** tab above\n\n"
                "If you believe this policy should be in the system, please request the administrator to add the official document to the knowledge repository."
            ),
            "citations": [],
        }

    # Build context string with citations labeled
    context = ""
    for i, chunk in enumerate(chunks):
        context += (
            f"\n[Source {i + 1}] Document: {chunk.get('source', '')}, "
            f"Page: {chunk.get('page', '')}\n{chunk.get('text', '')}\n"
        )

    user_prompt = f"""Context from Official VIT Pune Documents:
{context}

Student/User Question:
{question}

Please answer the student's question in a warm, structured, and human-friendly format based strictly on the official document excerpts above."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.25,
        )
        answer_text = response.choices[0].message.content
    except Exception as exc:
        # Fallback to raw chunk display
        answer_text = (
            "Here is what I found in the official VIT Pune documents:\n\n"
            + "\n\n".join(
                f"**{c.get('source')} (Page {c.get('page')}):**\n{c.get('text', '')[:400]}..."
                for c in chunks[:3]
            )
            + "\n\nFor further assistance, please visit **www.vit.edu** or contact the Student Section."
        )

    return {"answer": answer_text, "citations": citations}


def generate_conversational_response(message: str, intent: str = "greeting") -> str:
    """Generate a warm response for greetings ONLY. General inquiries now go through RAG."""
    client = _get_client()

    if intent == "greeting":
        greeting_fallback = (
            "Hello! 👋 Welcome to the **VIT Pune AI Copilot**.\n\n"
            "I can help you with questions about VIT Pune's **official policies and documents** — "
            "things like exam rules, CGPA calculations, fee structures, scholarships, and more.\n\n"
            "**What I can help with:**\n"
            "- 📋 Exam & assessment policies, CGPA/SGPA rules\n"
            "- 💰 Fee structure, MahaDBT scholarships, summer term registration\n"
            "- 👥 Student talent search — projects, internships, hackathons\n"
            "- 🔬 Research papers and patents across all engineering domains\n"
            "- 🎫 Submit grievance/complaint tickets\n\n"
            "**Note:** My answers are based only on the official documents uploaded to my knowledge base. "
            "For department-specific syllabi or faculty info, please visit **[www.vit.edu](https://www.vit.edu)**.\n\n"
            "What would you like to know?"
        )
        if not client:
            return greeting_fallback
        try:
            resp = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
                messages=[
                    {"role": "system", "content": (
                        "You are the VIT Pune AI Copilot. Give a warm welcome greeting. "
                        "Be clear that you ONLY answer from official VIT Pune documents and cannot make up information. "
                        "List what you can help with briefly."
                    )},
                    {"role": "user", "content": f"The student sent: '{message}'. Give a friendly welcome response."}
                ],
                temperature=0.5,
            )
            return resp.choices[0].message.content
        except Exception:
            return greeting_fallback

    # Fallback for any other intent
    return (
        "I'm here to help! Please ask me about VIT Pune's official policies, exam rules, fees, or use the tabs above "
        "to search the Talent Repository or Research papers."
    )
