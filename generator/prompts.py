# generator/prompts.py

ANSWER_PROMPT = """You must answer the question using ONLY the provided context.
If the context does not fully support a claim, do not make it.

Question:
{question}

Context:
{context}
"""

HEDGE_PROMPT = """The evidence is incomplete or conflicting.
Provide a cautious, qualified response.
Explicitly acknowledge uncertainty and do not invent details.

Question:
{question}

Context:
{context}
"""

REFUSAL_TEMPLATE = """I don’t have sufficient reliable information to answer this question.
"""
