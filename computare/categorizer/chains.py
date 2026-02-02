"""
LangChain chain definitions for transaction categorization.
"""

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from .prompts import BATCH_CATEGORIZATION_PROMPT, SINGLE_CATEGORIZATION_PROMPT
from .categories import TransactionCategory


def get_llm(model: str = "gpt-4o-mini", temperature: float = 0.0) -> ChatOpenAI:
    """
    Create the OpenAI LLM instance.

    API key is read from OPENAI_API_KEY environment variable.
    """
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def build_batch_chain():
    """
    Build the batch categorization chain.

    Input: {"count": int, "transactions_json": str, "categories": str}
    Output: dict with "results" key containing list of {raw, merchant, category}
    """
    llm = get_llm()
    parser = JsonOutputParser()

    chain = BATCH_CATEGORIZATION_PROMPT | llm | parser
    return chain


def build_single_chain():
    """
    Build the single-transaction categorization chain.

    Input: {"raw_store": str, "description": str, "categories": str}
    Output: dict with {merchant, category}
    """
    llm = get_llm()
    parser = JsonOutputParser()

    chain = SINGLE_CATEGORIZATION_PROMPT | llm | parser
    return chain


def get_categories_string() -> str:
    """Format all categories as a numbered list for prompt injection."""
    return "\n".join(
        f"{i + 1}. {cat.value}"
        for i, cat in enumerate(TransactionCategory)
    )
