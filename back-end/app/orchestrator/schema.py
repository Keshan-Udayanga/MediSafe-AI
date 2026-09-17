from pydantic import BaseModel, Field
from typing import List, Literal


class TaskStep(BaseModel):

    agent_target: Literal[
        "info_agent",
        "safety_agent"
    ]

    task_instruction: str


class ExecutionPlan(BaseModel):

    extracted_drugs: List[str] = Field(
        default_factory=list
    )

    reasoning: str

    steps: List[TaskStep] = Field(
        default_factory=list
    )

    requires_rag: bool = True