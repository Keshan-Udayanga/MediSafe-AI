from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

from app.agents.factory import (
    get_drug_info_agent,
    get_drug_safety_agent,
)
from app.orchestrator.router import (
    generate_execution_plan
)
from app.ir_module.rag import (
    retrieve_context,
)

from app.routes import auth_routes
from app.routes import document_routes


app = FastAPI(
    title="MediSafe AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_routes.router
)

app.include_router(
    document_routes.router
)


class ResearchRequest(BaseModel):

    query: str

    target_drugs: List[str] = Field(
        default_factory=list
    )


def get_agent_output(result) -> str:

    raw_output = (
        result["messages"][-1].content
    )

    if isinstance(raw_output, list):

        if raw_output:

            first_item = raw_output[0]

            if isinstance(
                first_item,
                dict
            ):

                return first_item.get(
                    "text",
                    str(first_item)
                )

            return str(first_item)

    return str(raw_output)


def build_rag_prompt(
        query: str,
        context: str,
        task_instruction: str,
    ) -> str:

        return f"""
    User Question:
    {query}

    Task:
    {task_instruction}

    Retrieved Documents:
    {context}

    STRICT INSTRUCTIONS:
    - Answer ONLY using the retrieved documents.
    - Do not use general knowledge or invent clinical facts.
    - If the document does not contain specific parameters, state "Data not available in source docs".

    OUTPUT FORMATTING RULES FOR R&D:
    1. Format the response as a professional **Technical Drug Profile**.
    2. Group the attributes into clear, logical research segments (e.g., Clinical Profile, Pharmacology, Regulatory & Commerce).
    3. Use high-density, analytical markdown formatting (clean bullet points, key bolding).
    4. Do not output raw JSON keys, unformatted text blocks, or conversational filler phrases.
    """



@app.post("/api/orchestrate")
async def orchestrate_research(
    payload: ResearchRequest,
):

    try:

        # ------------------------------------------------
        # 1. RETRIEVAL: this must happen before any agent is created.
        # ------------------------------------------------
        rag_result = retrieve_context(query=payload.query)

        # ------------------------------------------------
        # 3. HARD RELEVANCE GATE
        # ------------------------------------------------

        if not rag_result["has_context"]:

            return {
                "orchestrator_reasoning":
                    "No relevant medical document context was found.",

                "final_consolidated_answer":
                    rag_result["message"],

                "retrieved_documents": [],

                "detailed_steps": [],
            }

        # Routing is deterministic and only occurs after relevant context exists.
        plan = generate_execution_plan(
            payload.query,
            payload.target_drugs,
        )

        # ------------------------------------------------
        # 4. EXECUTE AGENTS
        # ------------------------------------------------

        accumulated_answers = []

        for index, step in enumerate(
            plan.steps
        ):

            if (
                step.agent_target
                == "info_agent"
            ):

                agent_executor = (
                    get_drug_info_agent()
                )

                agent_name = (
                    "Drug Information Agent"
                )

            elif (
                step.agent_target
                == "safety_agent"
            ):

                agent_executor = (
                    get_drug_safety_agent()
                )

                agent_name = (
                    "Drug Safety & Interaction Agent"
                )

            else:

                continue

            agent_prompt = build_rag_prompt(
                query=payload.query,
                context=rag_result["context"],
                task_instruction=(
                    step.task_instruction
                ),
            )

            result = (
                await agent_executor.ainvoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": agent_prompt,
                            }
                        ]
                    }
                )
            )

            output = get_agent_output(
                result
            )

            accumulated_answers.append(
                {
                    "step": index + 1,
                    "agent": agent_name,
                    "output": output,
                }
            )

        # ------------------------------------------------
        # 5. FINAL ANSWER
        # ------------------------------------------------

        if not accumulated_answers:

            return {
                "orchestrator_reasoning":
                    plan.reasoning,
                "final_consolidated_answer":
                    "No suitable agent was selected.",
                "retrieved_documents":
                    rag_result["documents"],
                "detailed_steps": [],
            }

        final_answer = (
            accumulated_answers[-1]["output"]
        )

        return {
            "orchestrator_reasoning":
                plan.reasoning,

            "final_consolidated_answer":
                final_answer,

            "retrieved_documents": [
                {
                    "document_id":
                        item["document_id"],

                    "title":
                        item["title"],

                    "document_type":
                        item["document_type"],

                    "score":
                        item["score"],

                    "chunk_id":
                        item["chunk_id"],
                }
                for item in rag_result[
                    "documents"
                ]
            ],

            "detailed_steps":
                accumulated_answers,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"RAG orchestration failed: "
                f"{type(exc).__name__}: {str(exc)}"
            ),
        )