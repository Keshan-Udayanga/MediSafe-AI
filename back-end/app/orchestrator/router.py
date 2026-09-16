
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.orchestrator.schema import ExecutionPlan

def generate_execution_plan(researcher_query: str) -> ExecutionPlan:
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
        ("human", "Researcher Query: {query}")
    ])
    
    # Invoke the structured chain
    chain = prompt | structured_llm
    return chain.invoke({"query": researcher_query})
