class Generator:
    def generate_answer(self, question: str, retrieved_context: str) -> str:
        """
        Later can route to LLM call.
        """
        if retrieved_context:
            return f"(Answer conditioned on retrieved context)\n\nQ: {question}\n\n[context used]\n{retrieved_context[:800]}"
        return f"(Answer from parametric knowledge)\n\nQ: {question}\n\n[no retrieval used]"