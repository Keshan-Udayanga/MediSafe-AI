
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.factory import get_drug_info_agent, get_drug_safety_agent

app = FastAPI(title="Pharmaceutical Multi-Agent Safety API")

class ResearchRequest(BaseModel):
    query: str
    target_drugs: List[str]

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
