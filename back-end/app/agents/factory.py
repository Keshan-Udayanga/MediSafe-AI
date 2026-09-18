from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from app.agents.config import (
    drug_info_config,
    drug_interaction_config,
    AgentConfig,
)


def create_gemini_agent(config: AgentConfig):

    llm = ChatGoogleGenerativeAI(
        model=config.model_name,
        max_retries=2,
    )

    system_prompt = (
        f"You are {config.name}, working as a {config.role}.\n"
        f"Your Goal: {config.goal}\n"
        f"Your Backstory: {config.backstory}\n\n"

        "STRICT RAG RULES:\n"
        "1. You may ONLY use information contained in the supplied retrieved context.\n"
        "2. Do NOT use your own general knowledge.\n"
        "3. Do NOT guess or infer unsupported medical facts.\n"
        "4. If the retrieved context does not contain enough information, "
        "say that the information is not available in the provided documents.\n"
        "5. Do not answer questions unrelated to the supplied medical documents.\n"
        "6. You must answer ONLY using the retrieved medical document context.\n"
        "7. If the answer is not supported by the retrieved context, say that the information is not available in the provided medical documents."
    )

    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=system_prompt,
    )

    return agent


def get_drug_info_agent():

    return create_gemini_agent(
        drug_info_config
    )


def get_drug_safety_agent():

    return create_gemini_agent(
        drug_interaction_config
    )