import os
import json
import requests
from datetime import datetime

# Target API URL (Top 50 Python repos by stars)
GITHUB_API_URL = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page=50"

def extract_bronze_data():
    """Fetches raw JSON payload from GitHub API and writes it to data/bronze/."""
    print("Starting Bronze Extraction from GitHub API...")
    
    # Send GET request with a custom User-Agent (GitHub API requirement)
    headers = {"User-Agent": "DataEngineeringPipeline/1.0"}
    response = requests.get(GITHUB_API_URL, headers=headers)
    
    # Check if request succeeded
    response.raise_for_status()
    raw_payload = response.json()
    
    # Determine local directory path (handles execution inside or outside container)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bronze_dir = os.path.join(base_dir, "data", "bronze")
    os.makedirs(bronze_dir, exist_ok=True)
    
    # Timestamped filename for auditability and idempotency
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(bronze_dir, f"raw_repos_{timestamp}.json")
    
    # Save unedited raw JSON payload
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(raw_payload, f, indent=2)
        
    print(f"Bronze Extraction successful! Raw JSON saved to: {file_path}")
    print(f"Total repositories ingested: {len(raw_payload.get('items', []))}")
    return file_path

if __name__ == "__main__":
    extract_bronze_data()