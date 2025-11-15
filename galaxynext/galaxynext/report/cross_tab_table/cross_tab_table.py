

import frappe
import re

def execute(filters=None):
    if not filters:
        filters = {}

    # 1️⃣ Get main report data
    columns, data_main = get_data_and_columns(filters)
    total_main = build_section_total(data_main, columns, "Total")

    # 2️⃣ Get customer-group summary
    data_summary = get_summary_data(filters, columns)
    total_summary = build_section_total(data_summary, columns, "Customer Group Total")

    # 3️⃣ Get company-wise summary
    data_company = get_company_summary_data(filters, columns)
    total_company = build_section_total(data_company, columns, "Company-wise Total")

    # 4️⃣ Build separator rows
    separator_row_summary = build_summary_header_row(columns)
    separator_row_company = build_company_header_row(columns)

    # 5️⃣ Combine all data
    final_data = (
        data_main
        + [total_main]
        + [separator_row_summary]
        + data_summary
        + [total_summary]
        + [separator_row_company]
        + data_company
        + [total_company]
    )

    return columns, final_data


# ======================================================
# 🔹 HEADER BUILDERS
# ======================================================
def build_summary_header_row(columns):
    row = {}
    row[columns[0]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Customer Group Summary</div>"
    for col in columns:
        if "/" in col["label"]:
            row[col["fieldname"]] = f"<div style='font-weight:bold;font-size:14px;text-align:center;'>{col['label']}</div>"
    row[columns[-1]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Total Amount</div>"
    return row


def build_company_header_row(columns):
    row = {}
    row[columns[0]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Company-wise Summary</div>"
    for col in columns:
        if "/" in col["label"]:
            row[col["fieldname"]] = f"<div style='font-weight:bold;font-size:14px;text-align:center;'>{col['label']}</div>"
    row[columns[-1]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Total Amount</div>"
    return row


# ======================================================
# 🔹 MAIN REPORT DATA
# ======================================================
def get_data_and_columns(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")

    results, colnames = call_stored_procedure("sp_get_sales_invoice_data", from_date, to_date)
    if not results:
        return [], []

    columns = []
    for idx, col in enumerate(colnames):
        col_lower = col.lower()
        is_month_col = "/" in col
        is_amount_col = "amount" in col_lower
        fieldtype = "HTML" if is_month_col or is_amount_col else "Data"
        width = 200 if is_month_col else 150

        columns.append({
            "label": col,
            "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
            "fieldtype": fieldtype,
            "width": width
        })

    data = []
    for row in results:
        row_dict = {}
        for idx, col in enumerate(colnames):
            val = row[idx]
            fieldname = col.lower().replace(" ", "_").replace("/", "_")

            if "/" in col:
                val = format_month_value(val)
            elif idx == len(colnames) - 1 and val:
                val = f"<div style='text-align:right;'>₹ {format_number(val)}</div>"

            row_dict[fieldname] = val
        data.append(row_dict)

    return columns, data


# ======================================================
# 🔹 SUMMARY + COMPANY SUMMARY
# ======================================================
def get_summary_data(filters, columns):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    results, colnames = call_stored_procedure("sp_get_sales_invoice_summary", from_date, to_date)
    return build_summary_rows(results, colnames)


def get_company_summary_data(filters, columns):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    results, colnames = call_stored_procedure("sp_get_sales_invoice_company_summary", from_date, to_date)
    return build_summary_rows(results, colnames)


def build_summary_rows(results, colnames):
    data = []
    for row in results:
        row_dict = {}
        for idx, col in enumerate(colnames):
            val = row[idx]
            fieldname = col.lower().replace(" ", "_").replace("/", "_")

            if "/" in col:
                val = format_month_value(val)
            elif idx == len(colnames) - 1 and val:
                val = f"<div style='text-align:right;'>₹ {format_number(val)}</div>"

            row_dict[fieldname] = val
        data.append(row_dict)
    return data


# ======================================================
# 🔹 SECTION TOTAL BUILDER
# ======================================================
def build_section_total(data, columns, label="Total"):
    if not data:
        return {}

    total_row = {}
    total_row[columns[0]["fieldname"]] = f"<b>{label}</b>"

    for col in columns[1:]:
        fname = col["fieldname"]
        label_text = col["label"]

        # Month columns (Q | R | A)
        if "/" in label_text:
            q_total, r_total, a_total = 0, 0, 0
            for row in data:
                html_val = str(row.get(fname, ""))
                q, r, a = extract_qra(html_val)
                q_total += q
                r_total += r
                a_total += a

            total_row[fname] = format_month_value(f"{q_total}|{r_total}|{a_total}")

        # Total Amount or numeric HTML
        elif "amount" in fname or "total" in fname:
            total = 0
            for row in data:
                total += extract_number(row.get(fname))
            total_row[fname] = f"<div style='text-align:right;font-weight:bold;'>₹ {format_number(total)}</div>"

        else:
            total_row[fname] = ""

    return total_row


# ======================================================
# 🔹 SAFE QRA EXTRACTOR (FIXED)
# ======================================================
def extract_qra(html_text):
    """Extract numeric values for Q, R, A specifically (avoids month label or stray numbers)"""
    try:
        q_match = re.search(r"Q:\s*([0-9,.]+)", html_text)
        r_match = re.search(r"R:\s*₹?\s*([0-9,.]+)", html_text)
        a_match = re.search(r"A:\s*₹?\s*([0-9,.]+)", html_text)

        q = float(q_match.group(1).replace(",", "")) if q_match else 0
        r = float(r_match.group(1).replace(",", "")) if r_match else 0
        a = float(a_match.group(1).replace(",", "")) if a_match else 0

        return q, r, a
    except:
        return 0, 0, 0


# ======================================================
# 🔹 NUMBER EXTRACTOR
# ======================================================
def extract_number(value):
    if not value:
        return 0
    try:
        match = re.search(r"[\d,.]+", str(value))
        if match:
            return float(match.group(0).replace(",", ""))
    except:
        pass
    return 0


# ======================================================
# 🔹 INLINE MONTH FORMATTER
# ======================================================
def format_month_value(value):
    if not value:
        return "<div style='text-align:center;'>-</div>"

    value = str(value).replace("₹", "").replace(",", "").strip()
    parts = re.split(r"[|, ]+", value)
    parts = [p.strip() for p in parts if p.strip()]

    qty = format_number(parts[0]) if len(parts) > 0 else "0.00"
    rate = format_number(parts[1]) if len(parts) > 1 else "0.00"
    amount = format_number(parts[2]) if len(parts) > 2 else "0.00"

    return f"""
    <div style='text-align:center;font-family:monospace;font-size:13px;'>
        Q: {qty} | R: ₹ {rate} | A: ₹ {amount}
    </div>
    """.strip()


# ======================================================
# 🔹 FORMAT NUMBER
# ======================================================
def format_number(num):
    try:
        return f"{float(num):,.2f}"
    except:
        return str(num)


# ======================================================
# 🔹 CALL STORED PROCEDURE
# ======================================================
def call_stored_procedure(proc_name, from_date, to_date):
    query = f"CALL {proc_name}(%s, %s)"
    conn = frappe.db.get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (from_date, to_date))
    results = cursor.fetchall()
    colnames = [d[0] for d in cursor.description] if cursor.description else []
    while cursor.nextset():
        pass
    cursor.close()
    conn.close()
    return results, colnames
    