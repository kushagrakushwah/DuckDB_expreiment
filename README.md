# 🧾 DuckDB Invoice Warehouse & EDA Layer

> A clean, fast, and serverless data foundation built for testing Small Language Models (**GLiNER** & **TabPFN**) on real-world financial documents.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/katanaml-org/invoices-donut-data-v1)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

---

### 👋 Hey Team!

Before diving into training models or writing complex prompts, we wanted to make sure we had a solid, trustworthy data foundation. 

Instead of playing with dummy text or synthetic mockups, this project pulls **50 real-world scanned invoices**, prepares them for our upcoming SLM harness, and stores everything in a local **DuckDB** warehouse that anyone can query in milliseconds without setting up a database server.

---

### ✨ What’s Inside?

* **🖼️ 50 Real Invoice Scans**: Downloaded from Katana ML's open-source Sparrow benchmark on Hugging Face. You can open and view all original scanned receipts and bills right inside [`data/real_invoices/images/`](data/real_invoices/images/).
* **📝 Dual Formats for SLMs**:
  * **Markdown Text**: Formatted with clear headings and key-value sections so **GLiNER** can pull out vendor names, dates, tax IDs, and totals.
  * **HTML Tables**: Clean `<table>` tags preserving line-item rows so **TabPFN** can inspect quantities, prices, and math.
* **⚡ Serverless DuckDB Warehouse**: All invoices, individual line items, and experiment logs are saved inside a single portable file (`data/slm_warehouse.duckdb`). No Docker, no open ports, and zero configuration required.
* **📊 Pre-run EDA Notebook**: A ready-to-share Jupyter notebook (`notebooks/01_duckdb_eda.ipynb`) packed with interactive SQL queries to evaluate data health, spend volumes, and scan qualities.

---

### 💡 What Did We Discover From the Data?

Running Exploratory Data Analysis (EDA) on the 50 real invoices gave us three important takeaways for our model pipeline:

| What We Checked | What the Data Showed | Why It Matters for Us |
| :--- | :--- | :--- |
| **Document Length** | Average **226 tokens**, Maximum **315 tokens** | GLiNER has a 512-token limit. Because every invoice is under 315 tokens, **we don't need any text chunking or sliding windows**. GLiNER can read each document in one pass! |
| **Field Types** | Currencies & tax rates repeat; descriptions are unique | Low-cardinality fields (currency, rates) can be parsed with instant Regex, while high-cardinality fields (vendors, items) get routed to GLiNER. |
| **Table Sizes** | 1 to 7 line items per invoice | Small tables are the exact sweet spot for **TabPFN**, giving us instant tabular predictions without training from scratch. |

---

### 📁 Project Structure

```text
duckdb implementation/
├── README.md                     # Project overview and guide
├── requirements.txt              # Required Python libraries
├── run_pipeline.py               # 1-click runner: downloads data, builds DB, runs EDA
│
├── data/
│   ├── real_invoices/            # 50 invoice JSONs + invoices_manifest.json
│   │   └── images/               # 50 real high-res invoice scans (.jpg)
│   └── slm_warehouse.duckdb      # Single-file persistent DuckDB database
│
├── src/
│   ├── fetch_real_invoices.py    # Pulls 50 real invoices from Hugging Face
│   ├── db.py                     # DuckDB schema and table setup
│   ├── ingest.py                 # Loads JSON records into DuckDB tables
│   └── eda.py                    # Analytical SQL queries and statistical reports
│
└── notebooks/
    └── 01_duckdb_eda.ipynb       # Interactive Jupyter analysis notebook
```

---

### 🚀 Getting Started in 2 Minutes

#### 1. Activate Environment
```powershell
..\.venv\Scripts\Activate.ps1
```

#### 2. Run the Full Pipeline
This verifies the real invoices, populates DuckDB, and prints out the EDA summary:
```powershell
python run_pipeline.py
```

#### 3. Open the Interactive Notebook
```powershell
jupyter lab notebooks/01_duckdb_eda.ipynb
```

---

### 🎯 Next Steps

Now that our data layer, real invoice scans, and DuckDB warehouse are live, the next phase is building the **DSPy harness** to connect **GLiNER** (for text spans) and **TabPFN** (for line-item validation), tracking all experiment scores directly in **MLflow**.
