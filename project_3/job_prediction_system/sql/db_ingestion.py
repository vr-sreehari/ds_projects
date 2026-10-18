"""
HR Analytics & Job Acceptance Prediction System
Database Ingestion Script (MySQL via SQLAlchemy)

Batches and loads cleaned candidate placement records into MySQL.
Supports configuration via environment variables, .env file, or CLI arguments.
"""

import os
import sys
import time
import argparse
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment configuration if available
load_dotenv()

# Default Database Configuration
DEFAULT_DB_USER = os.getenv("DB_USER", "root")
DEFAULT_DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DEFAULT_DB_HOST = os.getenv("DB_HOST", "localhost")
DEFAULT_DB_PORT = os.getenv("DB_PORT", "3306")
DEFAULT_DB_NAME = os.getenv("DB_NAME", "hr_analytics_db")
DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dataset",
    "cleaned_placement_data.csv"
)

def parse_args():
    parser = argparse.ArgumentParser(description="Ingest Cleaned Placement Dataset into MySQL Database")
    parser.add_argument("--user", default=DEFAULT_DB_USER, help="MySQL Database User")
    parser.add_argument("--password", default=DEFAULT_DB_PASSWORD, help="MySQL Database Password")
    parser.add_argument("--host", default=DEFAULT_DB_HOST, help="MySQL Database Host")
    parser.add_argument("--port", default=DEFAULT_DB_PORT, help="MySQL Database Port")
    parser.add_argument("--database", default=DEFAULT_DB_NAME, help="MySQL Database Name")
    parser.add_argument("--csv", default=DEFAULT_CSV_PATH, help="Path to cleaned placement CSV file")
    parser.add_argument("--batch-size", type=int, default=2500, help="Batch insertion chunk size")
    return parser.parse_args()

def create_db_engine(user, password, host, port, database):
    """Establishes connection to MySQL and ensures target database exists."""
    # First connect to server root to create database if not present
    server_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"
    engine_server = create_engine(server_url, isolation_level="AUTOCOMMIT")
    
    with engine_server.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
    
    # Connect to target database
    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(db_url, pool_pre_ping=True)

def ingest_data(args):
    start_time = time.time()
    print("=" * 70)
    print("🎯 Candidate Placement Dataset — Database Ingestion Engine")
    print("=" * 70)
    print(f"[*] CSV Source:      {args.csv}")
    print(f"[*] Target Host:     {args.host}:{args.port}")
    print(f"[*] Target Database: {args.database}")
    print(f"[*] Batch Chunk:     {args.batch_size:,} records/chunk")
    print("-" * 70)

    # 1. Verify CSV Existence
    if not os.path.exists(args.csv):
        print(f"[!] Error: Cleaned CSV file not found at: {args.csv}")
        sys.exit(1)

    print("[*] Loading CSV dataset into memory...")
    df = pd.read_csv(args.csv)
    total_records = len(df)
    print(f"[+] Loaded {total_records:,} records with {df.shape[1]} columns.")

    # 2. Establish Database Engine
    try:
        print("[*] Connecting to MySQL server and initializing schema...")
        engine = create_db_engine(args.user, args.password, args.host, args.port, args.database)
        print("[+] MySQL connection established successfully.")
    except Exception as e:
        print("\n[!] Database Connection Failed:")
        print(f"    {e}")
        print("\n💡 Troubleshooting Tips:")
        print("   1. Verify your MySQL server is running (e.g. `brew services start mysql` on macOS).")
        print("   2. Pass credentials via CLI or .env: python db_ingestion.py --user root --password YOUR_PASS")
        sys.exit(1)

    # 3. Batch Insert Records into MySQL
    table_name = "candidate_placements"
    print(f"[*] Ingesting records into table `{table_name}` in batches of {args.batch_size:,}...")
    
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",  # Ensures fresh ingestion
            index=True,
            index_label="candidate_id",
            chunksize=args.batch_size,
            method="multi"
        )
        print(f"[+] All {total_records:,} records successfully written to `{table_name}`.")
    except Exception as e:
        print(f"[!] Ingestion failed: {e}")
        sys.exit(1)

    # 4. Verify Record Count in Database
    with engine.connect() as conn:
        count_result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`;")).scalar()
        placed_count = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}` WHERE status = 1;")).scalar()
        dropout_count = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}` WHERE status = 0;")).scalar()

    elapsed = time.time() - start_time
    print("-" * 70)
    print("✅ Ingestion Verification Summary:")
    print(f"    - Total Rows in DB:       {count_result:,}")
    print(f"    - Accepted Offers (1):    {placed_count:,} ({placed_count/count_result*100:.2f}%)")
    print(f"    - Offer Dropouts (0):     {dropout_count:,} ({dropout_count/count_result*100:.2f}%)")
    print(f"    - Total Execution Time:   {elapsed:.2f} seconds")
    print("=" * 70)

if __name__ == "__main__":
    cli_args = parse_args()
    ingest_data(cli_args)
