import os
import glob
import json
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

# ==========================================
# 1. Pydantic Data Contract (Silver Layer)
# ==========================================
class RepositoryModel(BaseModel):
    id: int
    name: str
    full_name: str
    owner_login: str
    html_url: str
    description: Optional[str] = "No description"
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)
    language: Optional[str] = "Unknown"
    created_at: str
    updated_at: str

def transform_silver_data():
    """Reads latest Bronze file, validates records via Pydantic, routes bad data to DLQ, and writes clean Silver data."""
    print("Starting Silver Data Transformation & Validation...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bronze_dir = os.path.join(base_dir, "data", "bronze")
    silver_dir = os.path.join(base_dir, "data", "silver")
    dlq_dir = os.path.join(base_dir, "data", "dlq")
    
    os.makedirs(silver_dir, exist_ok=True)
    os.makedirs(dlq_dir, exist_ok=True)
    
    # Find the latest Bronze raw file
    bronze_files = glob.glob(os.path.join(bronze_dir, "raw_repos_*.json"))
    if not bronze_files:
        raise FileNotFoundError("No Bronze files found! Run 01_extract_bronze.py first.")
    
    latest_bronze_file = max(bronze_files, key=os.path.getmtime)
    print(f"Processing latest Bronze file: {latest_bronze_file}")
    
    with open(latest_bronze_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    items = raw_data.get("items", [])
    valid_records = []
    quarantined_records = []
    
    # Validate each item against the Data Contract
    for item in items:
        raw_record = {
            "id": item.get("id"),
            "name": item.get("name"),
            "full_name": item.get("full_name"),
            "owner_login": item.get("owner", {}).get("login") if isinstance(item.get("owner"), dict) else None,
            "html_url": item.get("html_url"),
            "description": item.get("description"),
            "stargazers_count": item.get("stargazers_count"),
            "forks_count": item.get("forks_count"),
            "open_issues_count": item.get("open_issues_count"),
            "language": item.get("language"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
        }
        
        try:
            validated_repo = RepositoryModel(**raw_record)
            valid_records.append(validated_repo.model_dump())
        except ValidationError as err:
            raw_record["validation_error"] = str(err)
            quarantined_records.append(raw_record)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save valid records to Silver
    silver_file_path = os.path.join(silver_dir, f"clean_repos_{timestamp}.json")
    with open(silver_file_path, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2)
        
    print(f"Silver Transformation complete! Clean records saved to: {silver_file_path}")
    print(f"Valid Records: {len(valid_records)}")
    
    # Quarantine bad records to DLQ if any exist
    if quarantined_records:
        dlq_file_path = os.path.join(dlq_dir, f"dlq_repos_{timestamp}.json")
        with open(dlq_file_path, "w", encoding="utf-8") as f:
            json.dump(quarantined_records, f, indent=2)
        print(f"WARNING: {len(quarantined_records)} bad records quarantined to DLQ: {dlq_file_path}")
    else:
        print("Zero data quality errors detected. DLQ remains empty.")
        
    return silver_file_path

if __name__ == "__main__":
    transform_silver_data()