import os 
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain.tools import tool

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@tool
async def get_drug_information(drug_name: str) -> str:
    """Retrieve verified information about a medication."""

    def _query():
        # Instantiate an isolated client instance for this specific database operation
        local_supabase = get_supabase_client()
        return (
            local_supabase
            .table("drugs")
            .select("*")
            .ilike("name", drug_name)
            .execute()
        )

    # Run safely in a background thread
    response = await asyncio.to_thread(_query)
    
    if not response.data:
        return f"No information found for {drug_name}"

    return str(response.data)

@tool
async def check_drug_safety(drug_name: str) -> str:
    """Retrieve verified safety information about a medication."""
    
    def _query():
        # Instantiate an isolated client instance for this specific database operation
        local_supabase = get_supabase_client()
        return (
            local_supabase
            .table("drug_interactions")
            .select("*")
            .or_(f"drug_a.ilike.{drug_name},drug_b.ilike.{drug_name}")
            .execute()
        )

    # Run safely in a background thread
    response = await asyncio.to_thread(_query)

    if not response.data:
        return f"No safety information found for {drug_name}."

    safety_information = response.data
    result = f"Safety information for {drug_name}:\n\n"

    # FIX: Map properties strictly to existing database columns
    for item in safety_information:
        result += f"Paired Compounds: {item.get('drug_a')} + {item.get('drug_b')}\n"
        result += f"Severity: {item.get('severity', 'N/A')}\n"
        result += f"Information/Description: {item.get('description', 'N/A')}\n\n"

    return result
