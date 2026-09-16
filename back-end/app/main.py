
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Any
from app.agents.factory import get_drug_info_agent, get_drug_safety_agent
from app.orchestrator.router import generate_execution_plan
from app.routes import auth_routes
from app.routes import document_routes
from app.database import engine, Base
from app import models

import logging

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

@app.post("/api/agents/info")
async def run_info_agent(payload: ResearchRequest):
    """Retrieves standard database records for selected compounds."""
    try:
        agent_executor = get_drug_info_agent()
        input_prompt = f"Fetch drug specifications and basic records for: {', '.join(payload.target_drugs)}. Additional Context: {payload.query}"
        

        payload_data = {
            "messages": [
                {"role": "user", "content": input_prompt}
            ]
        }
        result = await agent_executor.ainvoke(payload_data)
        # 1. Capture the raw response block
        raw_output = result["messages"][-1].content
        
        # 2. Extract cleanly if LangChain wrapped the text response inside a list element
        if isinstance(raw_output, list) and len(raw_output) > 0:
            agent_output = raw_output[0].get("text", str(raw_output))
        else:
            agent_output = str(raw_output)
        
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
        input_prompt = f"Run an extensive safety check and cross-reference interactions between: {', '.join(payload.target_drugs)}. Context/Researcher Query: {payload.query}"
        
        payload_data = {
            "messages": [
                {"role": "user", "content": input_prompt}
            ]
        }

        result = await agent_executor.ainvoke(payload_data)

        raw_output = result["messages"][-1].content

        if isinstance(raw_output, list) and len(raw_output) > 0:
            agent_output = raw_output[0].get("text", str(raw_output))
        else:
            agent_output = str(raw_output)
        
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
        plan = generate_execution_plan(payload.query)
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
            agent_input = f"{step.task_instruction}\n\nContext gathered so far:\n{accumulated_context}"
    
            payload_data = {
                "messages": [
                    {"role": "user", "content": agent_input}
                ]
            }
            # Execute the specific agent
            result = await agent_executor.ainvoke(payload_data)
            raw_output = result["messages"][-1].content

            if isinstance(raw_output, list) and len(raw_output) > 0:
                agent_output = raw_output[0].get("text", str(raw_output))
            else:
                agent_output = str(raw_output)

            
            # Update history context for subsequent agents in the flow
            accumulated_context += f"--- Output from Step {index+1} ({agent_name}) ---\n{agent_output}\n\n"
            
            execution_logs.append({
                "step": index + 1,
                "agent": agent_name,
                "instruction_given": step.task_instruction,
                "output": agent_output
            })
            
        return {
            "orchestrator_reasoning": plan.reasoning,
            "final_consolidated_answer": accumulated_context,
            "detailed_steps": execution_logs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration pipeline failed: {str(e)}")