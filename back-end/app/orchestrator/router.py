
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
            "Your job is to analyze the researcher's query and enforce the following strict clinical routing rules:\n\n"
            
            "1. RELEVANCE FILTER:\n"
            "- Evaluate if the query is strictly about medicine, pharmacology, or health. "
            "If it is about unrelated topics (e.g., coding, sports, weather, jokes), set 'is_drug_related' to false, leave 'extracted_drugs' and 'steps' completely empty.\n\n"
            
            "2. ENTITY EXTRACTION:\n"
            "- Extract all specific drug names, active ingredients, or chemical compounds into 'extracted_drugs'.\n"
            "- If the query is related to medicine but NO specific drug or compound is named anywhere in the prompt, leave 'extracted_drugs' and 'steps' empty.\n\n"
            
            "3. ROUTING AND AGENT SELECTION:\n"
            "- Available Agents: 'info_agent' (database lookups/properties) and 'safety_agent' (interactions/adverse effects).\n"
            "- CRITICAL RULE: If the user is ONLY looking for general drug properties or information, DO NOT use or schedule the 'safety_agent'. Schedule the 'info_agent' only.\n"
            "- If the user specifically asks about safety, warnings, or cross-interactions between multiple drugs, schedule the 'safety_agent' (either alone or after the info_agent).\n"
            "- Make sure the 'task_instruction' explicitly mentions which extracted drugs to process."
        ),
        ("human", "Researcher Query: {query}")
    ])
    
    # Invoke the structured chain
    chain = prompt | structured_llm
    return chain.invoke({"query": researcher_query})
