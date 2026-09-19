from app.orchestrator.schema import (
    ExecutionPlan,
    TaskStep,
)


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