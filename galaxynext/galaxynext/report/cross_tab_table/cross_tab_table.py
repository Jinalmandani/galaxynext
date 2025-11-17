# Copyright (c) 2025, kishan and contributors
# For license information, please see license.txt

# import frappe

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns, data = get_data_and_columns(filters)
    return columns, data


def get_data_and_columns(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")

    # Call the stored procedure
    results, colnames = call_stored_procedure(from_date, to_date)

    if not results:
        return [], []

    # Prepare ERPNext report column structure
    columns = []
    for col in colnames:
        col_lower = col.lower()
        
        # Check if this is a month column (contains /)
        is_month_column = "/" in col
        
        # For month columns, use Data type to show the concatenated string
        # For other amount/total columns, use Currency
        if is_month_column:
            fieldtype = "Data"
            width = 200  # Wider for concatenated values
        elif "amount" in col_lower or "total" in col_lower:
            fieldtype = "Currency"
            width = 150
        else:
            fieldtype = "Data"
            width = 150

        columns.append({
            "label": col.replace("_", " ").title(),
            "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
            "fieldtype": fieldtype,
            "width": width
        })

    # Convert results to list of dicts with proper fieldnames
    data = []
    for row in results:
        row_dict = {}
        for idx, col in enumerate(colnames):
            fieldname = col.lower().replace(" ", "_").replace("/", "_")
            row_dict[fieldname] = row[idx]
        data.append(row_dict)

    return columns, data


def call_stored_procedure(from_date, to_date):
    """
    Calls the MariaDB stored procedure sp_get_sales_invoice_data()
    which dynamically pivots month-wise totals.
    """
    query = "CALL sp_get_sales_invoice_data(%s, %s)"
    params = (from_date, to_date)

    conn = frappe.db.get_connection()
    cursor = conn.cursor()

    cursor.execute(query, params)

    # Fetch data
    results = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description] if cursor.description else []

    # Clear any remaining results (important for stored procedures)
    while cursor.nextset():
        pass

    cursor.close()
    conn.close()

    return results, colnames


