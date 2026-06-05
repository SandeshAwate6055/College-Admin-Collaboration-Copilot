from app.rag.generator import generate_answer


def test_generate_answer_returns_clear_message_without_groq_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    result = generate_answer(
        "What is CGPA?",
        [{"source": "policy.pdf", "page": 1, "text": "CGPA policy text"}],
    )

    assert "GROQ_API_KEY" in result["answer"]
    assert result["citations"] == [{"index": 1, "source": "policy.pdf", "page": 1}]
