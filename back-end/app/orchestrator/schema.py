
from pydantic import BaseModel, Field
from typing import List, Literal

class TaskStep(BaseModel):
    agent_target: Literal["info_agent", "safety_agent"] = Field(
        description="The specific agent that should handle this step."
    )
    task_instruction: str = Field(
        description="Clear, context-specific instructions telling this agent exactly what to search for or analyze."
    )

class ExecutionPlan(BaseModel):
    is_drug_related: bool = Field(
        description="Set to True if the query is strictly related to pharmacology, medicine, or biochemistry. Set to False for off-topic queries."
    )
    
    extracted_drugs: List[str] = Field(
        description="List of all unique pharmaceutical drug names, active compounds, or molecules extracted from the researcher's query."
    )
    
    reasoning: str = Field(
        description="Brief clinical justification for why this execution route and order was chosen."
    )
    steps: List[TaskStep] = Field(
        description="The ordered list of steps to execute sequentially."
    )
