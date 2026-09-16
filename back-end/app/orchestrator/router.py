
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.orchestrator.schema import ExecutionPlan, TaskStep

SAFETY_TERMS = (
    "interaction", "interactions", "contraindication", "contraindications",
    "side effect", "side effects", "adverse", "risk", "safety", "danger",
)


def _fallback_plan(researcher_query: str, target_drugs: list[str]) -> ExecutionPlan:
    query_lower = researcher_query.lower()
    drugs = list(dict.fromkeys(drug.strip() for drug in target_drugs if drug.strip()))
    safety_requested = any(term in query_lower for term in SAFETY_TERMS)
    info_requested = not safety_requested or any(
        term in query_lower for term in ("what is", "information", "uses", "dosage", "indication")
    )

    steps = []
    if info_requested:
        steps.append(TaskStep(
            agent_target="info_agent",
            task_instruction="Retrieve verified drug information relevant to the user's request.",
        ))
    if safety_requested:
        steps.append(TaskStep(
            agent_target="safety_agent",
            task_instruction="Check verified safety information, adverse effects, and interactions relevant to the user's request.",
        ))
    if not steps:
        steps.append(TaskStep(
            agent_target="info_agent",
            task_instruction="Retrieve verified drug information relevant to the user's request.",
        ))

    return ExecutionPlan(
        extracted_drugs=drugs,
        reasoning="Deterministic fallback routing was used because the planner did not return a usable plan.",
        steps=steps,
    )


def generate_execution_plan(
    researcher_query: str,
    target_drugs: list[str] | None = None,
) -> ExecutionPlan:
    """Uses Gemini to decide the workflow routing based on the user's research needs."""
    
    # Use pro for complex planning and reasoning
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    structured_llm = llm.with_structured_output(ExecutionPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are the Lead Scientific Orchestrator for a pharmaceutical multi-agent system.\n"
            "Your job is two-fold:\n"
            "1. Parse the researcher's query and extract all specific medication or drug names into 'extracted_drugs'.\n"
            "2. Break down the query into an ordered execution plan using the available agents.\n\n"
            "Available Agents:\n"
            "- info_agent: Best for fetching baseline molecular info, indications, and general properties from the database.\n"
            "- safety_agent: Best for cross-referencing combination interactions, warnings, and adverse reactions.\n\n"
            "Guidelines:\n"
            "- Ensure the extracted drug names are normalized (e.g., capitalized consistently or kept as standard generic names).\n"
            "- If no specific drugs are found, leave 'extracted_drugs' empty but direct the agent to handle the query safely.\n"
            "- Make sure the 'task_instruction' for each step explicitly tells the target agent which extracted drugs to look up."
        ),
        ("human", "Known Drugs: {drugs}\nResearcher Query: {query}")
    ])
    
    # Invoke the structured chain
    chain = prompt | structured_llm
    known_drugs = target_drugs or []

    try:
        plan = chain.invoke({
            "drugs": ", ".join(known_drugs),
            "query": researcher_query,
        })
        if plan and plan.steps:
            if known_drugs:
                plan.extracted_drugs = list(dict.fromkeys([
                    *known_drugs,
                    *plan.extracted_drugs,
                ]))
            return plan
    except Exception:
        pass

    return _fallback_plan(researcher_query, known_drugs)
