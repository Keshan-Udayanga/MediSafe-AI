import os 
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain.tools import tool

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

@tool
def get_drug_information(drug_name: str) -> str:
    """Retrieve verified information about a medication."""
    
    response = (
        supabase
        .table("drugs")
        .select("*")
        .ilike("name", drug_name)
        .execute()
    )

    if not response.data:
        return f"No information found for {drug_name}"

    return str(response.data)

@tool
def check_drug_safety(drug_name: str) -> str:
    """Retrieve verified safety information about a medication."""

    response = (
        supabase
        .table("drug_safety")
        .select("*")
        .ilike("drug_name", drug_name)
        .execute()
    )

    if not response.data:
        return f"No safety information found for {drug_name}."

    safety_information = response.data

    result = f"Safety information for {drug_name}:\n\n"

    for item in safety_information:
        result += f"Category: {item.get('category', 'N/A')}\n"
        result += f"Information: {item.get('description', 'N/A')}\n"
        result += f"Severity: {item.get('severity', 'N/A')}\n"
        result += f"Source: {item.get('source', 'N/A')}\n\n"

    return result