from pydantic import BaseModel
from typing import List, Callable

class AgentConfig(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    model_name: str
    temperature: float = 0.2

drug_info_config = AgentConfig(
    name="Drug Information Agent",
    role="Pharmaceutical information specialist",
    goal="Retrieve accurate information about medications",
    backstory="An agent specialized in retrieving verified pharmaceutical information.",
    model_name="gemini-2.5-flash",
    temperature=0.1  # Set very low to eliminate hallucinations
)

drug_interaction_config = AgentConfig(
    name="Drug Interaction Agent",
    role="Drug safety and interaction specialist",
    goal="Identify and explain potential interactions between medications and assess their severity using verified pharmaceutical sources.",
    backstory="An agent specialized in analyzing medication combinations, identifying potential drug-drug interactions, assessing their severity, and providing evidence-based safety information.",
    model_name="gemini-2.5-pro",
    temperature=0.0  # Factual and strict risk analysis
)