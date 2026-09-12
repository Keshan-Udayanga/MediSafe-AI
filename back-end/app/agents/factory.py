from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.config import drug_info_config, drug_interaction_config, AgentConfig
from app.tools import get_drug_information, check_drug_safety # Imported from your script

def create_gemini_agent(config: AgentConfig, tools: list) -> AgentExecutor:
    """Builds a structured LangChain tool agent bound to a specific Gemini model."""
    
    # 1. Initialize the specific Gemini model
    llm = ChatGoogleGenerativeAI(
        model=config.model_name,
        temperature=config.temperature,
        max_retries=2
    )
    
    # 2. Structure instructions safely for a clinical setting
    prompt = ChatPromptTemplate.from_messages([
        (
            "system", 
            f"You are {config.name}, working as a {config.role}.\n"
            f"Your Goal: {config.goal}\n"
            f"Your Backstory: {config.backstory}\n"
            f"CRITICAL: You are operating in a medical drug research development context. "
            f"Only rely on verified data outputs from your tools. Do not invent or assume safety warnings."
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 3. Create the executable tool calling pipeline
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Instantiations with their respective tools scoped
def get_drug_info_agent() -> AgentExecutor:
    return create_gemini_agent(drug_info_config, [get_drug_information])

def get_drug_safety_agent() -> AgentExecutor:
    # Interaction agent gets both tools to query profiles and check crossover safety flags
    return create_gemini_agent(drug_interaction_config, [get_drug_information, check_drug_safety])
