"""
DuckDB Database Manager for SLM Harness
Handles schema initialization, database connections, and utility queries.
"""

import os
from pathlib import Path
import duckdb

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "slm_warehouse.duckdb"

def get_connection(db_path: Path | str = DEFAULT_DB_PATH, read_only: bool = False):
    """
    Returns a connection to the persistent DuckDB warehouse.
    Creates parent directories if they don't exist.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(database=str(db_path), read_only=read_only)

def init_schema(conn: duckdb.DuckDBPyConnection):
    """
    Initializes all core schemas:
    1. raw_invoices: Original OCR data (Markdown & HTML) + ground truth metadata
    2. invoice_line_items: Tabular item-level breakdowns for TabPFN validation
    3. experiment_runs: Run-level tracking for hypothesis, parameters, and metrics
    4. extracted_entities: Fine-grained token/entity extraction outputs from GLiNER/DSPy
    """
    conn.execute("""
    -- 1. Raw Invoices Table (Source of Truth)
    CREATE TABLE IF NOT EXISTS raw_invoices (
        invoice_id VARCHAR PRIMARY KEY,
        file_name VARCHAR NOT NULL,
        vendor_name VARCHAR,
        invoice_date DATE,
        due_date DATE,
        currency VARCHAR(10) DEFAULT 'USD',
        subtotal DOUBLE,
        tax_amount DOUBLE,
        total_amount DOUBLE,
        line_items_count INTEGER,
        page_count INTEGER DEFAULT 1,
        document_quality_score DOUBLE, -- e.g. OCR confidence 0.0 to 1.0
        ocr_markdown TEXT,             -- Full text markdown from OCR
        ocr_html_tables TEXT,          -- HTML table tags extracted from invoice
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 2. Line Items Table (For Tabular Evaluation with TabPFN)
    CREATE TABLE IF NOT EXISTS invoice_line_items (
        item_id VARCHAR PRIMARY KEY,
        invoice_id VARCHAR REFERENCES raw_invoices(invoice_id),
        item_description VARCHAR,
        quantity DOUBLE,
        unit_price DOUBLE,
        line_total DOUBLE
    );

    -- 3. Experiment Runs Table (Tracking all pipeline iterations)
    CREATE TABLE IF NOT EXISTS experiment_runs (
        run_id VARCHAR PRIMARY KEY,
        hypothesis TEXT NOT NULL,
        pipeline_stage VARCHAR NOT NULL, -- 'OCR_INGESTION', 'GLINER_NER', 'TABPFN_TABLE', 'DSPY_HARNESS'
        model_name VARCHAR NOT NULL,
        parameters_json JSON,
        metrics_json JSON,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    );

    -- 4. Extracted Entities (GLiNER / DSPy outputs per invoice)
    CREATE TABLE IF NOT EXISTS extracted_entities (
        extraction_id VARCHAR PRIMARY KEY,
        run_id VARCHAR REFERENCES experiment_runs(run_id),
        invoice_id VARCHAR REFERENCES raw_invoices(invoice_id),
        entity_label VARCHAR NOT NULL,
        extracted_value VARCHAR,
        ground_truth_value VARCHAR,
        confidence_score DOUBLE,
        is_exact_match BOOLEAN,
        latency_ms DOUBLE
    );
    """)

if __name__ == "__main__":
    conn = get_connection()
    init_schema(conn)
    print(f"DuckDB schema successfully initialized at: {DEFAULT_DB_PATH}")
    conn.close()
