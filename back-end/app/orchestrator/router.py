
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.orchestrator.schema import ExecutionPlan

def generate_execution_plan(researcher_query: str, target_drugs: list[str]) -> ExecutionPlan:
    """Uses Gemini to decide the workflow routing based on the user's research needs."""
    
    # Use pro for complex planning and reasoning
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    structured_llm = llm.with_structured_output(ExecutionPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are the Lead Scientific Orchestrator for a pharmaceutical multi-agent system.\n"
            "Your job is to read a researcher's request and break it down into an ordered execution plan using the available agents.\n\n"
            "Available Agents:\n"
            "- info_agent: Best for fetching baseline molecular info, indications, and general properties of a drug.\n"
            "- safety_agent: Best for cross-referencing drug combinations, checking safety profiles, risks, and adverse reactions.\n\n"
            "Guidelines:\n"
            "1. If they ask about basic details AND safety/interactions, route to info_agent FIRST so the baseline data can be gathered, then route to safety_agent.\n"
            "2. If they only ask for interactions or safety, you may route straight to the safety_agent.\n"
            "3. Make sure the task_instruction explicitly mentions the drug names."
        ),
        ("human", "Target Drugs: {drugs}\nResearcher Query: {query}")
    ])
    
    # Invoke the structured chain
    chain = prompt | structured_llm
    return chain.invoke({"drugs": ", ".join(target_drugs), "query": researcher_query})
