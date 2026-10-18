"""
Fetch Real Invoices: Downloads 50 real invoice images and structured annotations
from the Katana ML Invoices Dataset on Hugging Face (katanaml-org/invoices-donut-data-v1).
Generates OCR Markdown and HTML Table representations for each real invoice.
"""

import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

DATASET_API_URL = "https://datasets-server.huggingface.co/rows?dataset=katanaml-org/invoices-donut-data-v1&config=default&split=train&offset=0&limit=100"

def clean_num(val) -> float:
    """Cleans currency strings into standard floats (e.g., '$37 153,67' -> 37153.67)."""
    if not val:
        return 0.0
    s = str(val).replace("$", "").replace("€", "").replace("£", "").strip()
    s = s.replace(" ", "")
    # Handle European decimal commas vs thousands commas
    if "," in s and "." in s:
        # e.g., 1,250.50
        s = s.replace(",", "")
    elif "," in s:
        # e.g., 214,41
        s = s.replace(",", ".")
    try:
        return round(float(s), 2)
    except ValueError:
        return 0.0

def fetch_50_real_invoices(base_dir: Path):
    real_invoices_dir = base_dir / "data" / "real_invoices"
    images_dir = real_invoices_dir / "images"
    real_invoices_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to Hugging Face Dataset: katanaml-org/invoices-donut-data-v1...")
    req = urllib.request.Request(DATASET_API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    raw_rows = data.get("rows", [])
    print(f"Fetched {len(raw_rows)} rows from dataset metadata. Selecting 50 valid invoices with line items...")

    valid_invoices = []
    
    for row_entry in raw_rows:
        if len(valid_invoices) >= 50:
            break
            
        row = row_entry.get("row", {})
        gt_raw = row.get("ground_truth", "")
        if not gt_raw:
            continue
            
        try:
            gt = json.loads(gt_raw).get("gt_parse", {})
        except json.JSONDecodeError:
            continue
            
        header = gt.get("header", {})
        summary = gt.get("summary", {})
        items = gt.get("items", [])
        
        invoice_no = header.get("invoice_no")
        seller = header.get("seller")
        
        # Filter out empty/invalid entries
        if not invoice_no or not seller or len(items) == 0:
            continue

        total_gross = clean_num(summary.get("total_gross_worth"))
        if total_gross <= 0.0:
            continue

        # Extract dates
        raw_date = header.get("invoice_date", "2026-01-15")
        try:
            # Check for mm/dd/yyyy or yyyy-mm-dd
            if "/" in raw_date:
                parts = raw_date.split("/")
                if len(parts) == 3:
                    inv_date = f"{parts[2]}-{int(parts[0]):02d}-{int(parts[1]):02d}"
                else:
                    inv_date = "2026-01-15"
            else:
                inv_date = raw_date
        except Exception:
            inv_date = "2026-01-15"

        # Download actual image
        img_info = row.get("image", {})
        img_url = img_info.get("src")
        img_filename = f"{invoice_no}.jpg"
        img_path = images_dir / img_filename
        
        if img_url and not img_path.exists():
            try:
                urllib.request.urlretrieve(img_url, img_path)
            except Exception as e:
                print(f"Could not download image for {invoice_no}: {e}")

        # Extract Vendor Name (first line or first words before address)
        vendor_name = seller.split("\n")[0]
        # If address is combined in one line, split before digits
        m = re.match(r"^([^\d]+)", vendor_name)
        if m:
            vendor_name = m.group(1).strip(", ")

        client = header.get("client", "Fint Enterprise Client")
        subtotal = clean_num(summary.get("total_net_worth")) or round(total_gross * 0.9, 2)
        tax_amount = clean_num(summary.get("total_vat")) or round(total_gross - subtotal, 2)

        # Parse line items
        parsed_items = []
        for idx, it in enumerate(items, 1):
            desc = it.get("item_desc", f"Item #{idx}")
            qty = clean_num(it.get("item_qty")) or 1.0
            unit_price = clean_num(it.get("item_net_price")) or round(clean_num(it.get("item_gross_worth")) / max(qty, 1.0), 2)
            line_total = clean_num(it.get("item_gross_worth")) or round(qty * unit_price, 2)
            
            parsed_items.append({
                "item_id": f"INV-{invoice_no}-ITEM-{idx}",
                "item_description": desc,
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": line_total
            })

        # 1. OCR Output: Markdown Representation
        md_lines = [
            f"# INVOICE",
            f"**Invoice Number:** {invoice_no}",
            f"**Invoice Date:** {inv_date}",
            f"**Seller / Vendor:** {seller}",
            f"**Seller Tax ID:** {header.get('seller_tax_id', 'N/A')}",
            f"**Client / Bill To:** {client}",
            f"**Client Tax ID:** {header.get('client_tax_id', 'N/A')}",
            f"**IBAN / Payment Ref:** {header.get('iban', 'N/A')}",
            f"",
            f"## Itemized Line Items",
            f"| Description | Qty | Net Unit Price | Line Gross Total |",
            f"| :--- | :---: | :---: | :---: |"
        ]
        for it in parsed_items:
            md_lines.append(f"| {it['item_description']} | {it['quantity']} | ${it['unit_price']:.2f} | ${it['line_total']:.2f} |")
        
        md_lines.extend([
            f"",
            f"**Subtotal (Net):** ${subtotal:.2f}",
            f"**Total Tax / VAT:** ${tax_amount:.2f}",
            f"**Total Gross Amount Due:** ${total_gross:.2f}",
            f"",
            f"---",
            f"*Source Image: data/real_invoices/images/{img_filename}*"
        ])
        ocr_markdown = "\n".join(md_lines)

        # 2. OCR Output: HTML Table Representation
        html_rows = "".join([
            f"<tr><td>{it['item_description']}</td><td>{it['quantity']}</td>"
            f"<td>{it['unit_price']:.2f}</td><td>{it['line_total']:.2f}</td></tr>"
            for it in parsed_items
        ])
        ocr_html = (
            f"<table class='invoice-table' id='table-{invoice_no}'>"
            f"<thead><tr><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr></thead>"
            f"<tbody>{html_rows}</tbody>"
            f"<tfoot>"
            f"<tr><td colspan='3'>Subtotal</td><td>{subtotal:.2f}</td></tr>"
            f"<tr><td colspan='3'>Tax / VAT</td><td>{tax_amount:.2f}</td></tr>"
            f"<tr><td colspan='3'><strong>Grand Total</strong></td><td><strong>{total_gross:.2f}</strong></td></tr>"
            f"</tfoot></table>"
        )

        inv_record = {
            "invoice_id": str(invoice_no),
            "file_name": img_filename,
            "vendor_name": vendor_name,
            "invoice_date": inv_date,
            "due_date": inv_date,
            "currency": "USD",
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total_amount": total_gross,
            "line_items_count": len(parsed_items),
            "page_count": 1,
            "document_quality_score": 0.95,
            "ocr_markdown": ocr_markdown,
            "ocr_html_tables": ocr_html,
            "line_items": parsed_items,
            "image_path": str(img_path.relative_to(base_dir)).replace("\\", "/")
        }

        # Save individual JSON
        with open(real_invoices_dir / f"{invoice_no}.json", "w", encoding="utf-8") as f:
            json.dump(inv_record, f, indent=2)

        valid_invoices.append(inv_record)

    manifest_path = real_invoices_dir / "invoices_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(valid_invoices, f, indent=2)

    print(f"\nSuccessfully downloaded and processed {len(valid_invoices)} real invoices!")
    print(f"  • Real Invoice Images: {images_dir}")
    print(f"  • Invoices Manifest: {manifest_path}")
    return valid_invoices

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    fetch_50_real_invoices(project_root)
