"""
Master Runner Script for SLM DuckDB & EDA Pipeline
Executes:
1. Sample Data Generation (50 invoices with OCR Markdown + HTML)
2. DuckDB Schema Initialization & Ingestion
3. Comprehensive Exploratory Data Analysis (EDA)
"""

import sys
import subprocess
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))

    from src.generate_sample_data import generate_50_invoices
    from src.ingest import ingest_invoices
    from src.eda import run_eda

    print("\n" + "="*80)
    print("STEP 1: Generating 50 Realistic Invoices (OCR Markdown + HTML Tables)")
    print("="*80)
    raw_data_dir = base_dir / "data" / "raw_invoices"
    generate_50_invoices(raw_data_dir)

    print("\n" + "="*80)
    print("STEP 2: Ingesting into DuckDB Warehouse")
    print("="*80)
    manifest_path = raw_data_dir / "invoices_manifest.json"
    ingest_invoices(manifest_path)

    print("\n" + "="*80)
    print("STEP 3: Running Exploratory Data Analysis (EDA) via DuckDB SQL Engine")
    print("="*80)
    run_eda(verbose=True)

    print("\n" + "="*80)
    print("SUCCESS: Pipeline Complete! All data & runs are stored in data/slm_warehouse.duckdb")
    print("Open notebooks/01_duckdb_eda.ipynb to review in Jupyter.")
    print("="*80)

if __name__ == "__main__":
    main()
