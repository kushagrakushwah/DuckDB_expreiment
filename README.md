# SLM Harness — DuckDB & EDA Data Layer

This repository contains the **Data Setup, Warehouse Layer, and Exploratory Data Analysis (EDA)** for the SLM (GLiNER + TabPFN) execution phase.

---

## 🎯 Architecture Overview

```text
[50 Sample Invoices]
         │
         ├──> OCR Engine ──> Markdown (Text Spans for GLiNER)
         │               ──> HTML Tables (Tabular Data for TabPFN)
         │
         ▼
[DuckDB Analytical Warehouse] (data/slm_warehouse.duckdb)
         │
         ├──> raw_invoices          (Source of truth: OCR text, HTML tables, metadata)
         ├──> invoice_line_items     (Line-item tabular breakdown)
         ├──> experiment_runs        (Hypotheses, parameters, evaluation metrics)
         └──> extracted_entities     (GLiNER/DSPy predictions vs ground truth)
         │
         ▼
[Exploratory Data Analysis & Harness]
         ├──> Fast SQL Aggregations (Sub-second vector engine)
         ├──> Context Window Feasibility Checks (Token counts)
         └──> Jupyter Evaluation Notebooks (Shared with Mentor/Lead)
```

---

## 📁 Project Structure

```text
SLM/
├── requirements.txt              # Locked dependencies (duckdb, pandas, pyarrow, tabulate, etc.)
├── run_pipeline.py               # Master end-to-end runner (Data Gen -> Ingest -> EDA)
├── README.md                     # Documentation & Architecture rationale
├── data/
│   ├── raw_invoices/             # 50 simulated invoice JSONs & manifest
│   └── slm_warehouse.duckdb      # Persistent DuckDB embedded warehouse
├── notebooks/
│   └── 01_duckdb_eda.ipynb       # Interactive Jupyter analysis notebook for review
└── src/
    ├── __init__.py
    ├── db.py                     # DuckDB connection & schema initialization
    ├── generate_sample_data.py   # Generates 50 realistic invoices with OCR text & HTML
    ├── ingest.py                 # Ingestion pipeline into DuckDB tables
    └── eda.py                    # Comprehensive analytical SQL queries & stats
```

---

## ⚡ Quickstart

### 1. Activate Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Run the Complete Pipeline
```powershell
python run_pipeline.py
```

### 3. Launch the Evaluation Notebook
```powershell
jupyter lab notebooks/01_duckdb_eda.ipynb
```
