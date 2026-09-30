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

class CorrectedQuerySchema(BaseModel):
    cleaned_query: str = Field(
        description="The original user query with any spelling mistakes, typos, or brand names of drugs corrected to their proper medical/generic standard names."
    )
    corrected_drugs: List[str] = Field(
        description="List of specific drug names that were found and corrected in the query. Empty if no corrections were needed."
    )