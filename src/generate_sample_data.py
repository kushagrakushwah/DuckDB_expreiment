"""
Sample Data Generator: 50 Real-World Invoice Samples
Simulates OCR outputs (Markdown + HTML Tables) matching Fint use-case specifications.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

VENDORS = [
    ("Acme Logistics Inc.", "102 Industrial Way, Austin, TX", "TAX-99214"),
    ("CloudScale Technologies", "450 Silicon Blvd, San Jose, CA", "TAX-44120"),
    ("Apex Office & Hardware", "88 Market St, Chicago, IL", "TAX-77812"),
    ("CyberShield Security Ltd.", "12 Wall St, New York, NY", "TAX-55291"),
    ("Starlight SaaS Systems", "33 Innovation Dr, Seattle, WA", "TAX-11029"),
    ("Quantum Data Services", "700 Tech Square, Cambridge, MA", "TAX-88231"),
    ("Vertex Industrial Supply", "501 Factory Lane, Detroit, MI", "TAX-33419"),
    ("BlueSky Consulting Group", "100 Peachtree St, Atlanta, GA", "TAX-66102"),
    ("OmniChannel Retail Solutions", "220 Broadway, Denver, CO", "TAX-99041"),
    ("Nova Telecom Services", "99 Fiber Way, Dallas, TX", "TAX-22874"),
]

ITEM_CATALOG = [
    ("Enterprise Cloud Storage (1TB/mo)", 120.00),
    ("Security Audit & Vulnerability Assessment", 2500.00),
    ("Software License - Professional Tier (Seats)", 45.00),
    ("Managed Database Hosting - Multi-Region", 850.00),
    ("Consulting Hours - Senior ML Engineer", 180.00),
    ("High-Performance Compute Node (hr)", 3.50),
    ("Network Egress & Transit Bandwidth", 0.08),
    ("Technical Support SLA - 24/7 Platinum", 500.00),
    ("Hardware Maintenance & Replacement Kit", 320.00),
    ("SSL/TLS Certificate Renewal (Annual)", 150.00),
]

def generate_invoice(index: int) -> dict:
    inv_num = f"INV-2026-{1000 + index}"
    vendor_name, vendor_addr, tax_id = random.choice(VENDORS)
    
    # Dates
    base_date = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 270))
    due_date = base_date + timedelta(days=random.choice([15, 30, 45, 60]))
    
    # Line items
    num_items = random.randint(1, 6)
    selected_items = random.sample(ITEM_CATALOG, num_items)
    line_items = []
    subtotal = 0.0
    
    for i, (desc, base_price) in enumerate(selected_items, 1):
        qty = random.choice([1, 2, 5, 10, 20, 50])
        unit_price = round(base_price * random.uniform(0.9, 1.1), 2)
        total = round(qty * unit_price, 2)
        subtotal += total
        line_items.append({
            "item_id": f"{inv_num}-ITEM-{i}",
            "item_description": desc,
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": total
        })
    
    subtotal = round(subtotal, 2)
    tax_rate = random.choice([0.05, 0.07, 0.0825, 0.10])
    tax_amount = round(subtotal * tax_rate, 2)
    total_amount = round(subtotal + tax_amount, 2)
    
    page_count = 1 if num_items <= 3 else (2 if num_items <= 5 else 3)
    quality_score = round(random.uniform(0.82, 0.99), 3)

    # 1. OCR Output: Markdown Representation
    markdown_lines = [
        f"# INVOICE",
        f"**Invoice Number:** {inv_num}",
        f"**Date:** {base_date.strftime('%Y-%m-%d')}",
        f"**Due Date:** {due_date.strftime('%Y-%m-%d')}",
        f"",
        f"## Vendor Information",
        f"**Vendor:** {vendor_name}",
        f"**Address:** {vendor_addr}",
        f"**Tax ID / GST:** {tax_id}",
        f"",
        f"## Bill To",
        f"**Customer:** Fint Enterprise Solutions",
        f"**Account ID:** FINT-ACC-{random.randint(100, 999)}",
        f"",
        f"## Line Items",
        f"| Item Description | Qty | Unit Price | Total |",
        f"| :--- | :---: | :---: | :---: |"
    ]
    for item in line_items:
        markdown_lines.append(f"| {item['item_description']} | {item['quantity']} | ${item['unit_price']:.2f} | ${item['line_total']:.2f} |")
    
    markdown_lines.extend([
        f"",
        f"**Subtotal:** ${subtotal:.2f}",
        f"**Tax Amount ({tax_rate*100:.1f}%):** ${tax_amount:.2f}",
        f"**Total Amount Due:** ${total_amount:.2f}",
        f"",
        f"---",
        f"*Thank you for your business! Payment terms: Net { (due_date - base_date).days } days.*"
    ])
    ocr_markdown = "\n".join(markdown_lines)

    # 2. OCR Output: HTML Table Representation (Crucial for TabPFN table validation)
    html_rows = "".join([
        f"<tr><td>{item['item_description']}</td><td>{item['quantity']}</td>"
        f"<td>{item['unit_price']:.2f}</td><td>{item['line_total']:.2f}</td></tr>"
        for item in line_items
    ])
    ocr_html = (
        f"<table class='invoice-table' id='table-{inv_num}'>"
        f"<thead><tr><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr></thead>"
        f"<tbody>{html_rows}</tbody>"
        f"<tfoot>"
        f"<tr><td colspan='3'>Subtotal</td><td>{subtotal:.2f}</td></tr>"
        f"<tr><td colspan='3'>Tax</td><td>{tax_amount:.2f}</td></tr>"
        f"<tr><td colspan='3'><strong>Grand Total</strong></td><td><strong>{total_amount:.2f}</strong></td></tr>"
        f"</tfoot></table>"
    )

    return {
        "invoice_id": inv_num,
        "file_name": f"{inv_num}.pdf",
        "vendor_name": vendor_name,
        "invoice_date": base_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "currency": "USD",
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "line_items_count": len(line_items),
        "page_count": page_count,
        "document_quality_score": quality_score,
        "ocr_markdown": ocr_markdown,
        "ocr_html_tables": ocr_html,
        "line_items": line_items
    }

def generate_50_invoices(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    all_invoices = []
    
    for i in range(1, 51):
        inv = generate_invoice(i)
        all_invoices.append(inv)
        
        # Save individual raw mock files
        inv_file = output_dir / f"{inv['invoice_id']}.json"
        with open(inv_file, "w", encoding="utf-8") as f:
            json.dump(inv, f, indent=2)
            
    summary_file = output_dir / "invoices_manifest.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_invoices, f, indent=2)
        
    print(f"Generated 50 realistic invoice samples with OCR Markdown & HTML in: {output_dir}")
    return all_invoices

if __name__ == "__main__":
    random.seed(42)  # Deterministic generation
    data_dir = Path(__file__).resolve().parent.parent / "data" / "raw_invoices"
    generate_50_invoices(data_dir)
