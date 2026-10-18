"""
Ingestion Pipeline: Ingests raw invoices and experimental data into DuckDB.
Demonstrates DuckDB's direct zero-copy file querying capabilities.
"""

import json
from pathlib import Path
from src.db import get_connection, init_schema

def ingest_invoices(manifest_path: Path):
    """
    Ingests invoice data from manifest JSON into DuckDB tables:
    - raw_invoices
    - invoice_line_items
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}. Run generate_sample_data.py first.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        invoices = json.load(f)

    conn = get_connection()
    init_schema(conn)

    print(f"Ingesting {len(invoices)} invoices into DuckDB...")

    # Clear existing data in reverse foreign key order for idempotent re-runs
    conn.execute("DELETE FROM extracted_entities;")
    conn.execute("DELETE FROM experiment_runs;")
    conn.execute("DELETE FROM invoice_line_items;")
    conn.execute("DELETE FROM raw_invoices;")

    for inv in invoices:
        conn.execute("""
            INSERT INTO raw_invoices (
                invoice_id, file_name, vendor_name, invoice_date, due_date,
                currency, subtotal, tax_amount, total_amount, line_items_count,
                page_count, document_quality_score, ocr_markdown, ocr_html_tables
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inv["invoice_id"], inv["file_name"], inv["vendor_name"], inv["invoice_date"], inv["due_date"],
            inv["currency"], inv["subtotal"], inv["tax_amount"], inv["total_amount"], inv["line_items_count"],
            inv["page_count"], inv["document_quality_score"], inv["ocr_markdown"], inv["ocr_html_tables"]
        ))

        for item in inv["line_items"]:
            conn.execute("""
                INSERT INTO invoice_line_items (
                    item_id, invoice_id, item_description, quantity, unit_price, line_total
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item["item_id"], inv["invoice_id"], item["item_description"],
                item["quantity"], item["unit_price"], item["line_total"]
            ))

    # Seed an initial baseline experiment run to demonstrate the experiment tracking layer
    conn.execute("DELETE FROM extracted_entities;")
    conn.execute("DELETE FROM experiment_runs;")

    run_id = "RUN-EXP-001"
    conn.execute("""
        INSERT INTO experiment_runs (
            run_id, hypothesis, pipeline_stage, model_name, parameters_json, metrics_json, completed_at
        ) VALUES (
            ?, 
            'Baseline zero-shot extraction using GLiNER (gliner_small-v2.1) on raw OCR markdown spans',
            'GLINER_NER',
            'urchade/gliner_small-v2.1',
            '{"threshold": 0.45, "labels": ["invoice_number", "vendor_name", "total_amount", "tax_amount"]}',
            '{"precision": 0.94, "recall": 0.91, "f1": 0.925, "mean_latency_ms": 142.5}',
            CURRENT_TIMESTAMP
        )
    """, (run_id,))

    # Insert sample extraction outputs linked to the first real invoice
    first_inv = invoices[0]
    first_id = first_inv["invoice_id"]
    first_vendor = first_inv.get("vendor_name", "Vendor")
    first_total = f"${first_inv.get('total_amount', 0.0):.2f}"

    conn.execute("""
        INSERT INTO extracted_entities (
            extraction_id, run_id, invoice_id, entity_label, extracted_value,
            ground_truth_value, confidence_score, is_exact_match, latency_ms
        ) VALUES 
        ('EXT-001', 'RUN-EXP-001', ?, 'invoice_number', ?, ?, 0.98, true, 138.2),
        ('EXT-002', 'RUN-EXP-001', ?, 'vendor_name', ?, ?, 0.96, true, 145.0),
        ('EXT-003', 'RUN-EXP-001', ?, 'total_amount', ?, ?, 0.89, false, 140.8);
    """, (
        first_id, first_id, first_id,
        first_id, first_vendor, first_vendor,
        first_id, first_total, first_total
    ))

    # Verify counts
    invoice_count = conn.execute("SELECT count(*) FROM raw_invoices;").fetchone()[0]
    items_count = conn.execute("SELECT count(*) FROM invoice_line_items;").fetchone()[0]
    runs_count = conn.execute("SELECT count(*) FROM experiment_runs;").fetchone()[0]

    print(f"Ingestion Complete:")
    print(f"  - raw_invoices: {invoice_count} rows")
    print(f"  - invoice_line_items: {items_count} rows")
    print(f"  - experiment_runs: {runs_count} rows")

    conn.close()

if __name__ == "__main__":
    manifest = Path(__file__).resolve().parent.parent / "data" / "raw_invoices" / "invoices_manifest.json"
    ingest_invoices(manifest)
