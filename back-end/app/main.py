
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from app.agents.factory import get_drug_info_agent, get_drug_safety_agent
from app.orchestrator.router import generate_execution_plan
from app.routes import auth_routes
from app.routes import document_routes
from app.database import engine, Base
from app import models

import logging
import traceback

# Suppress AFC deprecation warnings emitted by google-genai
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google_genai._models").setLevel(logging.ERROR)
logging.getLogger("google.generativeai").setLevel(logging.ERROR)

app = FastAPI(title="Pharmaceutical Multi-Agent Safety API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the authentication routes
app.include_router(auth_routes.router)
app.include_router(document_routes.router)

Base.metadata.create_all(bind=engine)

class ResearchRequest(BaseModel):
    query: str
    target_drugs: List[str] = Field(default_factory=list)


def get_agent_output(result) -> str:
    raw_output = result["messages"][-1].content
    if isinstance(raw_output, list) and raw_output:
        first_item = raw_output[0]
        return first_item.get("text", str(first_item)) if isinstance(first_item, dict) else str(first_item)
    return str(raw_output)


def build_agent_prompt(query: str, drugs: List[str], instruction: str) -> str:
    drug_context = ", ".join(drugs) if drugs else "No specific drug names were supplied."
    return (
        f"Original researcher query: {query}\n"
        f"Identified drugs: {drug_context}\n"
        f"Required task: {instruction}\n"
        "Use the available verified database tools and answer only from their results."
    )

@app.post("/api/agents/info")
async def run_info_agent(payload: ResearchRequest):
    """Retrieves standard database records for selected compounds."""
    try:
        agent_executor = get_drug_info_agent()
        input_prompt = build_agent_prompt(
            payload.query,
            payload.target_drugs,
            "Retrieve baseline drug information, uses, properties, and indications relevant to the query.",
        )

        payload_data = {
            "messages": [
                {"role": "user", "content": input_prompt}
            ]
        }
        result = await agent_executor.ainvoke(payload_data)
        # 1. Capture the raw response block
        agent_output = get_agent_output(result)
        
        return {
            "agent_name": "Drug Information Agent", 
            "output": agent_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Info Agent execution failed: {str(e)}")

@app.post("/api/agents/safety")
async def run_safety_agent(payload: ResearchRequest):
    """Analyzes strict combination parameters and safety classifications across selected drugs."""
    try:
        agent_executor = get_drug_safety_agent()
        input_prompt = build_agent_prompt(
            payload.query,
            payload.target_drugs,
            "Check interactions, contraindications, adverse effects, and safety risks relevant to the query.",
        )
        
        payload_data = {
            "messages": [
                {"role": "user", "content": input_prompt}
            ]
        }

        result = await agent_executor.ainvoke(payload_data)

        agent_output = get_agent_output(result)
        
        return {
            "agent_name": "Drug Interaction Agent", 
            "output": agent_output
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety Agent execution failed: {str(e)}")


@app.post("/api/orchestrate")
async def orchestrate_research(payload: ResearchRequest):
    try:
        # 1. Ask the Orchestrator to plan the route
        plan = generate_execution_plan(payload.query, payload.target_drugs)
        print("--- Orchestration Plan Generated ---")
        print(f"Extracted Drugs: {plan.extracted_drugs}")
        print(f"Reasoning: {plan.reasoning}")
        # Keep track of the shared context as agents run
        # Track shared context as agents execute
        accumulated_context = f"Initial Researcher Goal: {payload.query}\n"
        accumulated_context += f"Identified Compounds: {', '.join(plan.extracted_drugs)}\n\n"
        execution_logs = []
        
        # 2. Execute the steps sequentially
        for index, step in enumerate(plan.steps):
            if step.agent_target == "info_agent":
                agent_executor = get_drug_info_agent()
                agent_name = "Drug Information Agent"
            elif step.agent_target == "safety_agent":
                agent_executor = get_drug_safety_agent()
                agent_name = "Drug Safety & Interaction Agent"
            else:
                continue
                
            print(agent_name)
            # Combine the orchestrator's specific instruction with previous outputs
            agent_input = build_agent_prompt(
                payload.query,
                plan.extracted_drugs,
                f"{step.task_instruction}\nContext gathered so far:\n{accumulated_context}",
            )
    
            payload_data = {
                "messages": [
                    {"role": "user", "content": agent_input}
                ]
            }
            # Execute the specific agent
            result = await agent_executor.ainvoke(payload_data)
            agent_output = get_agent_output(result)

            
            # Update history context for subsequent agents in the flow
            accumulated_context += f"--- Output from Step {index+1} ({agent_name}) ---\n{agent_output}\n\n"
            
            execution_logs.append({
                "step": index + 1,
                "agent": agent_name,
                "instruction_given": step.task_instruction,
                "output": agent_output
            })
            
        final_answer = execution_logs[-1]["output"] if execution_logs else "No agent execution step was produced."
        return {
            "orchestrator_reasoning": plan.reasoning,
            "final_consolidated_answer": final_answer,
            "detailed_steps": execution_logs
        }
        
    except Exception as e:
        print("\n===== ORCHESTRATION ERROR =====")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        traceback.print_exc()
        print("===== END ERROR =====\n")

        raise HTTPException(
            status_code=500,
            detail=f"Orchestration pipeline failed: {type(e).__name__}: {str(e)}"
        )