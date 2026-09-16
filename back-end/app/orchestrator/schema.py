
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
    reasoning: str = Field(
        description="Brief clinical justification for why this execution route and order was chosen."
    )
    steps: List[TaskStep] = Field(
        description="The ordered list of steps to execute sequentially."
    )
