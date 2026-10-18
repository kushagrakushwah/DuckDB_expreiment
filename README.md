# SLM Harness — DuckDB & EDA Data Layer (Real Invoice Corpus)

This repository contains the **Data Setup, Warehouse Layer, and Exploratory Data Analysis (EDA)** for the SLM (GLiNER + TabPFN) execution phase, grounded in **50 real invoice images and structured document annotations**.

---

## 🌐 Dataset Origin & Provenance

* **Dataset Source**: [Katana ML Invoices Dataset on Hugging Face (`katanaml-org/invoices-donut-data-v1`)](https://huggingface.co/datasets/katanaml-org/invoices-donut-data-v1)
* **Real Documents**: 50 full-resolution invoice images downloaded to [`data/real_invoices/images/`](file:///c:/Users/kusha/OneDrive/Music/Documents/Projects/SLM/duckdb%20implementation/data/real_invoices/images).
* **Ground-Truth Annotations**: Extracted directly from real invoice headers, seller/client details, tax IDs, itemized billing tables, and gross totals.

---

## 🎯 Architecture Overview

```text
[50 Real Invoice Images] (data/real_invoices/images/*.jpg)
         │
         ├──> OCR Ingestion ──> Markdown (Text Spans for GLiNER)
         │                  ──> HTML Tables (Tabular Data for TabPFN)
         │
         ▼
[DuckDB Analytical Warehouse] (data/slm_warehouse.duckdb)
         │
         ├──> raw_invoices          (Source of truth: OCR text, HTML tables, metadata, image paths)
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
duckdb implementation/
├── requirements.txt              # Locked dependencies (duckdb, pandas, pyarrow, tabulate, etc.)
├── run_pipeline.py               # Master end-to-end runner (Real Data Ingest -> DuckDB -> EDA)
├── README.md                     # Documentation & Dataset provenance
├── data/
│   ├── real_invoices/            # 50 real invoice JSONs + manifest
│   │   ├── images/               # 50 real downloaded invoice JPG images
│   │   │   ├── 12456262.jpg
│   │   │   └── ...
│   │   ├── 12456262.json
│   │   └── invoices_manifest.json
│   └── slm_warehouse.duckdb      # Persistent DuckDB embedded warehouse
├── notebooks/
│   └── 01_duckdb_eda.ipynb       # Interactive Jupyter analysis notebook for review
└── src/
    ├── __init__.py
    ├── db.py                     # DuckDB connection & schema initialization
    ├── fetch_real_invoices.py    # Downloads 50 real invoices and images from Hugging Face
    ├── ingest.py                 # Ingestion pipeline into DuckDB tables
    └── eda.py                    # Comprehensive analytical SQL queries & stats
```

---

## ⚡ Quickstart

### 1. Activate Environment
```powershell
..\.venv\Scripts\Activate.ps1
```

### 2. Run the Complete Real Data Pipeline
```powershell
python run_pipeline.py
```

### 3. Launch the Evaluation Notebook
```powershell
jupyter lab notebooks/01_duckdb_eda.ipynb
```
