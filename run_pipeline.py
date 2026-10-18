"""
Master Runner Script for SLM DuckDB & EDA Pipeline
Executes:
1. Real Invoices Ingestion (50 real invoice images + ground truth OCR Markdown & HTML)
   Source: Katana ML / HuggingFace Dataset (katanaml-org/invoices-donut-data-v1)
2. DuckDB Schema Initialization & Ingestion
3. Comprehensive Exploratory Data Analysis (EDA)
"""

import sys
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))

    from src.fetch_real_invoices import fetch_50_real_invoices
    from src.ingest import ingest_invoices
    from src.eda import run_eda

    real_data_dir = base_dir / "data" / "real_invoices"
    manifest_path = real_data_dir / "invoices_manifest.json"

    print("\n" + "="*80)
    print("STEP 1: Checking Real Invoices Dataset (HuggingFace: katanaml-org/invoices-donut-data-v1)")
    print("="*80)
    if not manifest_path.exists():
        fetch_50_real_invoices(base_dir)
    else:
        print(f"Real invoices already downloaded at: {real_data_dir}")
        print(f"Images directory: {real_data_dir / 'images'}")

    print("\n" + "="*80)
    print("STEP 2: Ingesting Real Invoices into DuckDB Warehouse")
    print("="*80)
    ingest_invoices(manifest_path)

    print("\n" + "="*80)
    print("STEP 3: Running Exploratory Data Analysis (EDA) on Real Data via DuckDB SQL Engine")
    print("="*80)
    run_eda(verbose=True)

    print("\n" + "="*80)
    print("SUCCESS: Real Invoice Pipeline Complete!")
    print(f"  • Real Invoice Images: {real_data_dir / 'images'}")
    print(f"  • DuckDB File: {base_dir / 'data' / 'slm_warehouse.duckdb'}")
    print(f"  • Jupyter Review: notebooks/01_duckdb_eda.ipynb")
    print("="*80)

if __name__ == "__main__":
    main()
