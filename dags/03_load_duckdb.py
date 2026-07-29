import os
import glob
import duckdb

# Target container paths inside /opt/airflow
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/opt/airflow/data/gold/github_analytics.duckdb")
SILVER_DATA_DIR = os.getenv("SILVER_DATA_DIR", "/opt/airflow/data/silver")

def load_silver_to_duckdb():
    # Guarantee output folder exists
    os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)
    
    json_files = glob.glob(os.path.join(SILVER_DATA_DIR, "*.json"))
    con = duckdb.connect(DUCKDB_PATH)
    
    if not json_files:
        print(f"⚠️ No JSON files found in {SILVER_DATA_DIR}. Initializing empty 'raw_repos' table structure.")
        con.execute("""
            CREATE TABLE IF NOT EXISTS raw_repos (
                id BIGINT,
                name VARCHAR,
                full_name VARCHAR,
                stargazers_count INT,
                forks_count INT,
                open_issues_count INT,
                updated_at VARCHAR,
                owner_login VARCHAR,
                extracted_at TIMESTAMP
            );
        """)
    else:
        print(f"📦 Loading {len(json_files)} silver JSON files into DuckDB...")
        con.execute("DROP TABLE IF EXISTS raw_repos;")
        con.execute(f"""
            CREATE TABLE raw_repos AS 
            SELECT *, current_timestamp AS extracted_at 
            FROM read_json_auto('{SILVER_DATA_DIR}/*.json');
        """)
        count = con.execute("SELECT COUNT(*) FROM raw_repos").fetchone()[0]
        print(f"✅ Successfully loaded {count} total records into 'raw_repos' table in DuckDB.")
        
    con.close()

if __name__ == "__main__":
    load_silver_to_duckdb()