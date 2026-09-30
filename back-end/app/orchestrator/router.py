from app.orchestrator.schema import (
    ExecutionPlan,
    TaskStep,
    CorrectedQuerySchema,
)

from app.agents.config import query_corrector_config
from app.agents.factory import get_query_corrector_agent

def fallback_plan(
    query: str,
    target_drugs: list[str]
) -> ExecutionPlan:

    query_lower = query.lower()
    
    safety_terms = [
        "interaction",
        "interactions",
        "side effect",
        "side effects",
        "adverse",
        "contraindication",
        "contraindications",
        "warning",
        "safety",
        "danger",
    ]

    safety_requested = any(
        term in query_lower
        for term in safety_terms
    )

    if safety_requested:

        steps = [
            TaskStep(
                agent_target="safety_agent",
                task_instruction=(
                    "Use only the retrieved safety-related "
                    "document context."
                ),
            )
        ]

    else:

        steps = [
            TaskStep(
                agent_target="info_agent",
                task_instruction=(
                    "Use only the retrieved drug information "
                    "document context."
                ),
            )
        ]

    return ExecutionPlan(
        extracted_drugs=[
            drug.strip()
            for drug in target_drugs
            if drug.strip()
        ],
        reasoning="Fallback routing plan.",
        steps=steps,
        requires_rag=True,
    )


def generate_execution_plan(
    researcher_query: str,
    target_drugs: list[str] | None = None,
) -> ExecutionPlan:
    return fallback_plan(researcher_query, target_drugs or [])


def clean_user_query(user_query: str) -> CorrectedQuerySchema:
    """Uses the custom query corrector agent from the factory to sanitize typos."""
    
    # 1. Fetch the corrector agent brain from the factory
    llm = get_query_corrector_agent()
    
    # 2. Bind the schema located inside your orchestrator/schema file
    structured_llm = llm.with_structured_output(CorrectedQuerySchema)
    
    # 3. Supply the persona constraints from your config file
    system_instruction = (
        f"You are the {query_corrector_config.name}, acting as a {query_corrector_config.role}.\n"
        f"Goal: {query_corrector_config.goal}\n"
        f"Backstory: {query_corrector_config.backstory}\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- Only fix structural errors, accidental typos, or common misspellings in pharmaceutical compounds/medications.\n"
        "- Retain original sentences, syntax structures, formatting, and prompt grammar perfectly.\n"
        "- If the query contains no recognizable typos or no drug names, return the text unchanged."
    )
    
    # 4. Invoke the clean structured pass
    response = structured_llm.invoke([
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_query}
    ])
    
    return response