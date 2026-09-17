
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
from app.agents.factory import get_drug_info_agent, get_drug_safety_agent
from app.orchestrator.router import generate_execution_plan

import logging

# Suppress AFC deprecation warnings emitted by google-genai
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google_genai._models").setLevel(logging.ERROR)
logging.getLogger("google.generativeai").setLevel(logging.ERROR)

app = FastAPI(title="Pharmaceutical Multi-Agent Safety API")

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

         # RULE 1: Ignore non-drug related inputs entirely
        if not plan.is_drug_related:
            return {
                "status": "ignored",
                "message": "Query ignored. This system only handles queries related to pharmaceutical research and drug data.",
                "orchestrator_reasoning": plan.reasoning
            }
            
        # RULE 2: Drug related, but missing required entities
        if not plan.extracted_drugs or len(plan.extracted_drugs) == 0:
            return {
                "status": "validation_failed",
                "message": "Please state any specific drug name or compound to continue.",
                "orchestrator_reasoning": plan.reasoning
            }
        
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

            last_message = result["messages"][-1]
            
            # 2. Extract content checking both object attributes and dictionary keys safely
            if hasattr(last_message, "content"):
                raw_output = last_message.content
            elif isinstance(last_message, dict):
                raw_output = last_message.get("content", "")
            else:
                raw_output = str(last_message)

            if isinstance(raw_output, list):
                # Handle block structures (e.g. text blocks from Gemini/OpenAI tools)
                parts = []
                for block in raw_output:
                    if isinstance(block, dict) and "text" in block:
                        parts.append(block["text"])
                    elif isinstance(block, str):
                        parts.append(block)
                agent_output = "\n".join(parts) if parts else str(raw_output)
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
            "status": "success",
            "extracted_drugs": plan.extracted_drugs,
            "orchestrator_reasoning": plan.reasoning,
            "final_consolidated_answer": accumulated_context,
            "detailed_steps": execution_logs
        }
        
    except Exception as e:
        import traceback
        print("---!!! DETAILED ORCHESTRATION PIPELINE CRASH !!!---")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Orchestration pipeline failed: {str(e)}")