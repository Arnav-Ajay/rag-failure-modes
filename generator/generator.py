# generator/generator.py
from __future__ import annotations
from typing import Optional

from policies.generation_policy import GenerationDecision
from generator.prompts import (
    ANSWER_PROMPT,
    HEDGE_PROMPT,
    REFUSAL_TEMPLATE,
)

class Generator:
    """
    Policy-gated generation.
    This class NEVER decides whether to generate.
    """

    def generate(
        self,
        *,
        question: str,
        context: str,
        decision: GenerationDecision,
        llm_call,  # injected callable
    ) -> Optional[str]:

        if decision.decision == "refuse":
            return REFUSAL_TEMPLATE

        if decision.decision == "hedge":
            prompt = HEDGE_PROMPT.format(
                question=question,
                context=context,
            )
        else:
            prompt = ANSWER_PROMPT.format(
                question=question,
                context=context,
            )

        response = llm_call(prompt)
        return response
