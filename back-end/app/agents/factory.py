from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents.config import drug_info_config, drug_interaction_config, AgentConfig
from app.tools import supabase_tools # Imported from your script

def create_gemini_agent(config: AgentConfig, tools: list) :
    """Builds a structured LangChain tool agent bound to a specific Gemini model."""
    
    # 1. Initialize the specific Gemini model
    llm = ChatGoogleGenerativeAI(
        model=config.model_name,
        max_retries=2
    )
    
    # 2. Structure instructions safely for a clinical setting
    system_prompt = (
        f"You are {config.name}, working as a {config.role}.\n"
        f"Your Goal: {config.goal}\n"
        f"Your Backstory: {config.backstory}\n"
        f"CRITICAL: You are operating in a medical drug research development context. "
        f"Only rely on verified data outputs from your tools. Do not invent or assume safety warnings."
    )

    # 3. Create the executable tool calling pipeline
    agent = create_agent(
        model=llm,          # Positional arg 1
        tools=tools,        # Positional arg 2
        system_prompt=system_prompt  # Keyword-only arg
    )
    return agent

# Instantiations with their respective tools scoped
def get_drug_info_agent():
    return create_gemini_agent(drug_info_config, [supabase_tools.get_drug_information])

def get_drug_safety_agent():
    # Interaction agent gets both tools to query profiles and check crossover safety flags
    return create_gemini_agent(drug_interaction_config, [supabase_tools.get_drug_information, supabase_tools.check_drug_safety])
