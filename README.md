# DuckDB Invoice Warehouse & Data Analysis

Hey everyone! This repository is the data foundation for our SLM (Small Language Model) invoice processing project. 

Instead of jumping straight into training or testing models on random fake text, we wanted to build a clean, real-world data layer first. We fetched 50 real scanned invoice images and their actual text annotations, converted them into clean formats, and loaded everything into DuckDB.

---

### What Does This Project Do?

In simple words, this project takes messy invoice documents and turns them into clean, structured data that anyone on the team can query in milliseconds.

1. **Real Invoice Scans**: We downloaded 50 real invoice images from the open-source Katana ML Sparrow dataset on Hugging Face. You can open and view all the original scans inside the `data/real_invoices/images/` folder.
2. **Prepared for Small Models**: We converted each invoice into two simple formats:
   * **Markdown text**: Great for testing **GLiNER** to pull out things like vendor names, invoice numbers, and dates.
   * **HTML tables**: Great for testing **TabPFN** to check line items, prices, and math.
3. **Stored in DuckDB**: Everything is saved in a single, fast local database file (`slm_warehouse.duckdb`). You don't need to install any heavy database server like PostgreSQL or MySQL—DuckDB runs directly inside Python with zero setup.
4. **Data Health Check (EDA)**: We wrote automated SQL checks to measure text lengths and review vendor distributions. We found that our longest invoice is around 315 tokens, which easily fits inside GLiNER's 512-token limit without cutting off any text.

---

### Folder Structure

Here is how the project is organized:

* `data/real_invoices/images/` — Contains all 50 real invoice pictures (`.jpg`).
* `data/real_invoices/` — Contains the structured JSON files for each invoice and a complete manifest.
* `data/slm_warehouse.duckdb` — The local DuckDB database file containing all tables.
* `src/` — Python scripts to download the data (`fetch_real_invoices.py`), set up the database (`db.py`), load the data (`ingest.py`), and run the analysis (`eda.py`).
* `notebooks/01_duckdb_eda.ipynb` — An interactive Jupyter notebook with pre-written SQL queries to explore the dataset visually.
* `run_pipeline.py` — A single runner script that sets up everything from start to finish.

---

### How to Run It Locally

You only need Python installed.

1. **Activate the virtual environment**:
   ```bash
   ..\.venv\Scripts\Activate.ps1
   ```

2. **Run the entire pipeline**:
   ```bash
   python run_pipeline.py
   ```

3. **Explore in Jupyter**:
   ```bash
   jupyter lab notebooks/01_duckdb_eda.ipynb
   ```

Feel free to explore the notebook, run your own queries on `slm_warehouse.duckdb`, or view the invoice images!
