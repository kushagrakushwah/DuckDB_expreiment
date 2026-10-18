"""
Exploratory Data Analysis (EDA) Module using DuckDB.
Computes comprehensive statistical, structural, and text-distribution metrics
over the 50-sample invoice dataset.
"""

from pathlib import Path
from tabulate import tabulate
from src.db import get_connection

def run_eda(verbose: bool = True):
    conn = get_connection(read_only=True)
    report_sections = []

    def section(title: str, query: str):
        df = conn.execute(query).df()
        table_str = tabulate(df, headers="keys", tablefmt="github", showindex=False)
        report_sections.append(f"### {title}\n```sql\n{query.strip()}\n```\n\n{table_str}\n")
        if verbose:
            print(f"\n{'='*70}\n {title}\n{'='*70}")
            print(table_str)
        return df

    # 1. High-Level Dataset Summary
    section(
        "1. Overall Dataset Overview",
        """
        SELECT 
            COUNT(*) AS total_invoices,
            MIN(invoice_date) AS earliest_date,
            MAX(invoice_date) AS latest_date,
            ROUND(SUM(total_amount), 2) AS gross_total_amount,
            ROUND(AVG(total_amount), 2) AS avg_invoice_amount,
            ROUND(MIN(total_amount), 2) AS min_amount,
            ROUND(MAX(total_amount), 2) AS max_amount,
            ROUND(AVG(document_quality_score), 3) AS avg_ocr_quality
        FROM raw_invoices;
        """
    )

    # 2. Text & Document Structural Distribution
    section(
        "2. OCR Document Structure & Token Length Analysis",
        """
        SELECT 
            page_count,
            COUNT(*) AS invoice_count,
            ROUND(AVG(LENGTH(ocr_markdown)), 0) AS avg_md_chars,
            ROUND(AVG(LENGTH(ocr_markdown) / 4.0), 0) AS est_avg_tokens,
            ROUND(MIN(LENGTH(ocr_markdown)), 0) AS min_md_chars,
            ROUND(MAX(LENGTH(ocr_markdown)), 0) AS max_md_chars,
            ROUND(AVG(LENGTH(ocr_html_tables)), 0) AS avg_html_chars
        FROM raw_invoices
        GROUP BY page_count
        ORDER BY page_count;
        """
    )

    # 3. Vendor Breakdown & Billing Volume
    section(
        "3. Top Vendors by Invoiced Amount & Volume",
        """
        SELECT 
            vendor_name,
            COUNT(*) AS invoice_count,
            ROUND(SUM(total_amount), 2) AS total_billed,
            ROUND(AVG(total_amount), 2) AS avg_invoice_value,
            ROUND(AVG(document_quality_score), 3) AS avg_scan_quality
        FROM raw_invoices
        GROUP BY vendor_name
        ORDER BY total_billed DESC;
        """
    )

    # 4. Line Items Granularity (Tabular Evaluation Pre-check)
    section(
        "4. Line Items Distribution & Quantities",
        """
        SELECT 
            line_items_count,
            COUNT(*) AS invoice_count,
            ROUND(AVG(subtotal), 2) AS avg_subtotal,
            ROUND(AVG(tax_amount), 2) AS avg_tax
        FROM raw_invoices
        GROUP BY line_items_count
        ORDER BY line_items_count;
        """
    )

    # 5. Top Line Item Descriptions in the Corpus
    section(
        "5. Most Frequent Billed Line Items",
        """
        SELECT 
            item_description,
            COUNT(*) AS frequency,
            ROUND(AVG(quantity), 1) AS avg_qty,
            ROUND(AVG(unit_price), 2) AS avg_unit_price,
            ROUND(SUM(line_total), 2) AS cumulative_spend
        FROM invoice_line_items
        GROUP BY item_description
        ORDER BY frequency DESC, cumulative_spend DESC;
        """
    )

    # 6. Quality & Outlier Detection
    section(
        "6. Low-Confidence Scans / Potential OCR Noise Outliers (< 0.88)",
        """
        SELECT 
            invoice_id,
            vendor_name,
            total_amount,
            page_count,
            document_quality_score
        FROM raw_invoices
        WHERE document_quality_score < 0.88
        ORDER BY document_quality_score ASC;
        """
    )

    # 7. Experiment Runs Verification
    section(
        "7. Experiment Runs & Extraction Harness State",
        """
        SELECT 
            run_id,
            model_name,
            pipeline_stage,
            json_extract_string(metrics_json, '$.f1') AS f1_score,
            json_extract_string(metrics_json, '$.mean_latency_ms') AS mean_latency_ms,
            hypothesis
        FROM experiment_runs;
        """
    )

    conn.close()
    return "\n".join(report_sections)

if __name__ == "__main__":
    run_eda()
