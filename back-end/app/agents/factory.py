# app/agents/factory.py
from lang import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents.config import analyst_agent_config
from app.tools.supabase_tools import fetch_user_profile

def get_data_analyst_agent() -> AgentExecutor:
    # 1. Provide the LLM brain
    llm = ChatOpenAI(model=analyst_agent_config.model_name, temperature=analyst_agent_config.temperature)
    
    # 2. Hand over database tools
    tools = [fetch_user_profile]
    
    # 3. Inject persona into the prompt layout
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are {analyst_agent_config.name}, the {analyst_agent_config.role}. Goal: {analyst_agent_config.goal}. Backstory: {analyst_agent_config.backstory}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 4. Compile into an executable agent instance
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
