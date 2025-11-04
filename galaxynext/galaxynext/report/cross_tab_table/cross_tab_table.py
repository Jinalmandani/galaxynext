
# ------------------------------------without store procedure----------------------------------

# import frappe

# def execute(filters=None):
#     if not filters:
#         filters = {}
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data

# def get_columns(filters):
#     months = frappe.db.sql_list("""
#         SELECT DISTINCT DATE_FORMAT(posting_date, '%%b/%%y')
#         FROM `tabSales Invoice`
#         WHERE docstatus = 1
#         AND posting_date BETWEEN %(from_date)s AND %(to_date)s
#         ORDER BY posting_date
#     """, filters)
    
#     cols = [
# 		{"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company" ,"width": 200},
#         {"fieldname": "customer_group", "label": "Customer Group", "fieldtype": "Data", "width": 200},
#         {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 200}
#     ]
    
#     for m in months:
#         month_key = m.lower().replace("/", "_").replace(" ", "_")
#         cols.append({
#             "fieldname": month_key,
#             "label": m,
#             "fieldtype": "HTML",
#             "width": 250
#         })
    
#     cols.append({
#         "fieldname": "total",
#         "label": "Total",
#         "fieldtype": "Currency",
#         "width": 120
#     })
    
#     return cols

# def format_value(amount, qty, rate):
#     """Format Amount, Qty and Rate with bold labels in horizontal format"""
#     amount_str = f"{amount:,.2f}" if amount else "0.00"
#     qty_str = f"{qty:,.2f}" if qty else "0.00"
#     rate_str = f"{rate:,.2f}" if rate else "0.00"
   
#     html = f"""
#     <div style="display:flex; justify-content:space-between; gap:10px; font-size:12px;">
#         <span><b>A:</b>₹{amount_str}</span>
#         <span><b>Q:</b>{qty_str}</span>
#         <span><b>R:</b>₹{rate_str}</span>
#     </div>
#     """
#     return html

# def get_data(filters):
#     result = frappe.db.sql("""
#         SELECT
#             si.customer,
#             si.customer_name,
# 			si.company,
#             c.customer_group,
#             DATE_FORMAT(si.posting_date, '%%b/%%y') as month,
#             SUM(si.total_qty) as total_qty,
#             AVG(sii.base_rate) as avg_rate,
#             SUM(si.base_total) as base_amount,
#             SUM(si.rounded_total) as rounded_amount
#         FROM `tabSales Invoice` si
#         LEFT JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         LEFT JOIN `tabCustomer` c ON c.name = si.customer
#         WHERE si.docstatus = 1
#         AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
#         GROUP BY si.company,c.customer_group, si.customer, month
#         ORDER BY si.company,c.customer_group, si.customer, si.posting_date
#     """, filters, as_dict=True)
    
#     customer_map = {}
   
#     for r in result:
#         key = (r.company,r.customer_group, r.customer)
#         if key not in customer_map:
#             customer_map[key] = {
# 				"company": r.company,
#                 "customer_group": r.customer_group,
#                 "customer": r.customer_name,
#                 "total": 0  # Initialize total directly
#             }
       
#         month_key = r.month.lower().replace("/", "_").replace(" ", "_")
       
#         # Format: A:Amount | Q:Qty | R:Rate
#         customer_map[key][month_key] = format_value(r.base_amount, r.total_qty, r.avg_rate)
       
#         # Add rounded_total to total
#         customer_map[key]["total"] += r.rounded_amount
    
#     return list(customer_map.values())



# ------------------------------------with store procedure----------------------------------


# import frappe
# from frappe import _

# def execute(filters=None):
#     if not filters:
#         filters = {}
    
#     columns = get_columns(filters)
#     data = get_data(filters)
    
#     return columns, data

# def call_stored_procedure(procedure_name, params):
#     """
#     Safely call stored procedure and handle multiple result sets
#     This prevents connection pool corruption
#     """
#     # Get a fresh connection from pool
#     conn = frappe.db._conn
    
#     try:
#         # Create a new cursor
#         cursor = conn.cursor()
        
#         # Build procedure call
#         placeholders = ', '.join(['%s'] * len(params))
#         query = f"CALL {procedure_name}({placeholders})"
        
#         # Execute procedure
#         cursor.execute(query, params)
        
#         # Fetch results from first result set
#         results = cursor.fetchall()
#         columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
#         # CRITICAL: Consume all remaining result sets to prevent corruption
#         while cursor.nextset():
#             pass
        
#         cursor.close()
        
#         # Convert to list of dicts
#         data = []
#         for row in results:
#             data.append(dict(zip(columns, row)))
        
#         return data
        
#     except Exception as e:
#         frappe.log_error(f"Stored Procedure Error: {str(e)}", "SP Call Failed")
#         # Rollback and reconnect to fix connection
#         frappe.db.rollback()
#         frappe.db.connect()
#         raise

# def get_columns(filters):
#     """Get dynamic columns using stored procedure"""
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")
    
#     # Call stored procedure safely
#     months = call_stored_procedure('sp_get_sales_invoice_months', [from_date, to_date])
    
#     # Extract month values
#     month_list = [m['month'] for m in months] if months else []
    
#     cols = [
#         # {
#         #     "fieldname": "company",
#         #     "label": _("Company"),
#         #     "fieldtype": "Link",
#         #     "options": "Company",
#         #     "width": 200
#         # },
#         {
#             "fieldname": "customer_group",
#             "label": _("Customer Group"),
#             "fieldtype": "Data",
#             "width": 200
#         },
#         {
#             "fieldname": "customer",
#             "label": _("Customer"),
#             "fieldtype": "Link",
#             "options": "Customer",
#             "width": 200
#         }
#     ]
    
#     # Add dynamic month columns
#     for month in month_list:
#         month_key = month.lower().replace("/", "_").replace(" ", "_")
#         cols.append({
#             "fieldname": month_key,
#             "label": month,
#             "fieldtype": "HTML",
#             "width": 250
#         })
    
#     # Add total column
#     cols.append({
#         "fieldname": "total",
#         "label": _("Total"),
#         "fieldtype": "Currency",
#         "width": 120
#     })
    
#     return cols

# def format_value(amount, qty, rate):
#     """Format Amount, Qty and Rate with bold labels in horizontal format"""
#     amount_str = f"{amount:,.2f}" if amount else "0.00"
#     qty_str = f"{qty:,.2f}" if qty else "0.00"
#     rate_str = f"{rate:,.2f}" if rate else "0.00"
    
#     html = f"""
#     <div style="display:flex; justify-content:space-between; gap:10px; font-size:12px;">
#         <span><b>A:</b>₹{amount_str}</span>
#         <span><b>Q:</b>{qty_str}</span>
#         <span><b>R:</b>₹{rate_str}</span>
#     </div>
#     """
#     return html

# def get_data(filters):
#     """Get sales invoice data using stored procedure"""
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")
    
#     # Call stored procedure safely
#     result = call_stored_procedure('sp_get_sales_invoice_data', [from_date, to_date])
    
#     customer_map = {}
    
#     for row in result:
#         key = ( row['customer_group'], row['customer'])
        
#         if key not in customer_map:
#             customer_map[key] = {
#                 # "company": row['company'],
#                 "customer_group": row['customer_group'],
#                 "customer": row['customer_name'],
#                 "total": 0
#             }
        
#         # Generate month key
#         month_key = row['month'].lower().replace("/", "_").replace(" ", "_")
        
#         # Format: A:Amount | Q:Qty | R:Rate
#         customer_map[key][month_key] = format_value(
#             row['base_amount'],
#             row['total_qty'],
#             row['avg_rate']
#         )
        
#         # Add to total
#         customer_map[key]["total"] += row['rounded_amount']
    
#     return list(customer_map.values())


# ------------------------------------dynamic store procedure----------------------------------


# import frappe
# from frappe import _

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     data, columns = get_data_and_columns(filters)
#     return columns, data


# def call_stored_procedure(procedure_name, params):
#     """Call stored procedure safely and get both data + column names"""
#     conn = frappe.db._conn
#     try:
#         cursor = conn.cursor()
#         placeholders = ', '.join(['%s'] * len(params))
#         query = f"CALL {procedure_name}({placeholders})"
#         cursor.execute(query, params)

#         results = cursor.fetchall()
#         columns = [desc[0] for desc in cursor.description] if cursor.description else []

#         # Important: clear remaining result sets
#         while cursor.nextset():
#             pass
#         cursor.close()

#         data = [dict(zip(columns, row)) for row in results]
#         return data, columns

#     except Exception as e:
#         frappe.log_error(f"Stored Procedure Error: {str(e)}", "SP Call Failed")
#         frappe.db.rollback()
#         frappe.db.connect()
#         raise


# def get_data_and_columns(filters):
#     """Auto-build columns dynamically from stored procedure"""
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     result, column_names = call_stored_procedure('sp_get_sales_invoice_data', [from_date, to_date])

#     columns = []

#     for col in column_names:
#         col_lower = col.lower()

#         # Auto field type detection
#         if "amount" in col_lower or "total" in col_lower or "rate" in col_lower:
#             fieldtype = "Currency"
#             width = 120
#         elif "qty" in col_lower:
#             fieldtype = "Float"
#             width = 100
#         elif "date" in col_lower or "month" in col_lower:
#             fieldtype = "Data"
#             width = 120
#         elif "company" in col_lower:
#             fieldtype = "Link"
#             width = 180
#         elif "customer" in col_lower:
#             fieldtype = "Link"
#             width = 200
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "fieldname": col_lower,
#             "label": _(col.replace("_", " ").title()),
#             "fieldtype": fieldtype,
#             "options": "Company" if "company" in col_lower else ("Customer" if "customer" in col_lower else ""),
#             "width": width
#         })

#     return result, columns


# ------------------------------------both sp----------------------------------


# import frappe
# from frappe import _

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     data, columns = get_data_and_columns(filters)
#     return columns, data


# def call_stored_procedure(procedure_name, params):
#     """Safely call stored procedure and handle multiple result sets"""
#     conn = frappe.db._conn
#     try:
#         cursor = conn.cursor()
#         placeholders = ', '.join(['%s'] * len(params))
#         query = f"CALL {procedure_name}({placeholders})"
#         cursor.execute(query, params)

#         results = cursor.fetchall()
#         columns = [desc[0] for desc in cursor.description] if cursor.description else []

#         # Clear remaining result sets (important in MariaDB/MySQL)
#         while cursor.nextset():
#             pass
#         cursor.close()

#         data = [dict(zip(columns, row)) for row in results]
#         return data, columns

#     except Exception as e:
#         frappe.log_error(f"Stored Procedure Error: {str(e)}", "SP Call Failed")
#         frappe.db.rollback()
#         frappe.db.connect()
#         raise


# def get_data_and_columns(filters):
#     """Dynamically build report columns + data using two stored procedures"""

#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     # ✅ 1. Get dynamic months list
#     month_data, month_cols = call_stored_procedure("sp_get_sales_invoice_months", [from_date, to_date])
#     months = [m["month"] for m in month_data] if month_data else []

#     # ✅ 2. Get main sales data
#     result, column_names = call_stored_procedure("sp_get_sales_invoice_data", [from_date, to_date])

#     # ✅ 3. Build columns dynamically
#     columns = []

#     for col in column_names:
#         col_lower = col.lower()

#         # Auto-detect types
#         if "amount" in col_lower or "total" in col_lower or "rate" in col_lower:
#             fieldtype = "Currency"
#             width = 120
#         elif "qty" in col_lower:
#             fieldtype = "Float"
#             width = 100
#         elif "date" in col_lower or "month" in col_lower:
#             fieldtype = "Data"
#             width = 120
#         elif "company" in col_lower:
#             fieldtype = "Link"
#             width = 180
#         elif "customer" in col_lower:
#             fieldtype = "Link"
#             width = 200
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "fieldname": col_lower,
#             "label": _(col.replace("_", " ").title()),
#             "fieldtype": fieldtype,
#             "options": "Company" if "company" in col_lower else ("Customer" if "customer" in col_lower else ""),
#             "width": width
#         })

#     # ✅ 4. Add month columns dynamically
#     for month in months:
#         month_key = month.lower().replace("/", "_").replace(" ", "_")
#         columns.append({
#             "fieldname": month_key,
#             "label": month,
#             "fieldtype": "Currency",
#             "width": 130
#         })

#     # ✅ 5. Add total column
#     columns.append({
#         "fieldname": "total",
#         "label": _("Total"),
#         "fieldtype": "Currency",
#         "width": 130
#     })

#     return result, columns

# -----------------------------------1---------------

# import frappe

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns, data = get_data_and_columns(filters)
#     return columns, data


# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     # Call the stored procedure
#     results, colnames = call_stored_procedure(from_date, to_date)

#     if not results:
#         return [], []

#     # Prepare ERPNext report column structure
#     columns = []
#     for col in colnames:
#         col_lower = col.lower()

#         # Detect Currency Columns
#         if (
#             "amount" in col_lower
#             or "total" in col_lower
#             or "rate" in col_lower
#             or "/" in col  # 👈 month columns like "Oct/25" also show as currency
#         ):
#             fieldtype = "Currency"
#         else:
#             fieldtype = "Data"

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_"),
#             "fieldtype": fieldtype,
#             "width": 150
#         })

#     return columns, results


# def call_stored_procedure(from_date, to_date):
#     """
#     Calls the MariaDB stored procedure sp_get_sales_invoice_data()
#     which dynamically pivots month-wise totals.
#     """
#     query = "CALL sp_get_sales_invoice_data(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)

#     # Fetch data
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     # Clear any remaining results (important for stored procedures)
#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames

# ----------------------------------------2----------------------------



# import frappe

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns, data = get_data_and_columns(filters)
#     return columns, data


# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     # Call the stored procedure
#     results, colnames = call_stored_procedure(from_date, to_date)

#     if not results:
#         return [], []

#     # Prepare ERPNext report column structure
#     columns = []
#     for col in colnames:
#         col_lower = col.lower()
        
#         # Check if this is a month column (contains /)
#         is_month_column = "/" in col
        
#         # For month columns, use Data type to show the concatenated string
#         # For other amount/total columns, use Currency
#         # if is_month_column:
#         #     fieldtype = "Data"
#         #     width = 200  # Wider for concatenated values

#         if is_month_column:
#             fieldtype = "HTML"
#             width = 220

#         elif "amount" in col_lower or "total" in col_lower:
#             fieldtype = "Currency"
#             width = 150
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     # Convert results to list of dicts with proper fieldnames
#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             row_dict[fieldname] = row[idx]
#         data.append(row_dict)

#     return columns, data


# def call_stored_procedure(from_date, to_date):
#     """
#     Calls the MariaDB stored procedure sp_get_sales_invoice_data()
#     which dynamically pivots month-wise totals.
#     """
#     query = "CALL sp_get_sales_invoice_data(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)

#     # Fetch data
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     # Clear any remaining results (important for stored procedures)
#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames

# ---------------------------------------------------------------------

# import frappe
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns, data = get_data_and_columns(filters)
#     return columns, data


# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     # Call the stored procedure
#     results, colnames = call_stored_procedure(from_date, to_date)

#     if not results:
#         return [], []

#     # Prepare ERPNext report column structure
#     columns = []
#     for col in colnames:
#         col_lower = col.lower()
        
#         # Check if this is a month column (contains /)
#         is_month_column = "/" in col

#         if is_month_column:
#             fieldtype = "HTML"  # Changed to HTML for custom formatting
#             width = 300
#         elif "amount" in col_lower or "total" in col_lower:
#             fieldtype = "Currency"
#             width = 150
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     # Convert results to list of dicts with proper fieldnames
#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             value = row[idx]
            
#             # Format month columns with pipe separator and right alignment
#             if "/" in col and value:
#                 value = str(value).strip()
#                 # Remove existing rupee symbols and clean up
#                 value = value.replace('₹', '').strip()
#                 # Split by multiple spaces
#                 parts = [p.strip() for p in re.split(r'\s+', value) if p.strip()]
                
#                 if len(parts) >= 3:
#                     qty = parts[0]
#                     rate = parts[1]
#                     amount = parts[2]
                    
#                     # Create HTML with right-aligned layout and fixed width spans
#                     html_value = f'''
#                     <div style="display: flex; align-items: center; font-family: monospace; font-size: 13px;">
#                         <span style="text-align: right; min-width: 80px; display: inline-block;">{qty}</span>
#                         <span style="margin: 0 8px;">|</span>
#                         <span style="text-align: right; min-width: 90px; display: inline-block;">₹ {rate}</span>
#                         <span style="margin: 0 8px;">|</span>
#                         <span style="text-align: right; min-width: 90px; display: inline-block;">₹ {amount}</span>
#                     </div>
#                     '''
#                     value = html_value.strip()
            
#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return columns, data


# def call_stored_procedure(from_date, to_date):
#     """
#     Calls the MariaDB stored procedure sp_get_sales_invoice_data()
#     which dynamically pivots month-wise totals.
#     """
#     query = "CALL sp_get_sales_invoice_data(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)

#     # Fetch data
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     # Clear any remaining results (important for stored procedures)
#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames






# summary report



# import frappe
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     # 1️⃣ Get first (main) table
#     columns, data_main = get_data_and_columns(filters)

#     # 2️⃣ Get second (summary) table
#     data_summary = get_summary_rows(filters, columns)

#     # 3️⃣ Add HTML separator row
#     separator_row = {
#         columns[0]["fieldname"]: "<div style='font-weight:bold;font-size:14px;margin-top:10px;'>Summary Report</div>"
#     }

#     # Combine both tables vertically
#     final_data = data_main + [separator_row] + data_summary

#     return columns, final_data


# # -------------------------------
# # MAIN REPORT (Stored Procedure)
# # -------------------------------
# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     results, colnames = call_stored_procedure(from_date, to_date)

#     if not results:
#         return [], []

#     columns = []
#     for col in colnames:
#         col_lower = col.lower()
#         is_month_col = "/" in col

#         if is_month_col:
#             fieldtype = "HTML"
#             width = 300
#         elif "amount" in col_lower or "total" in col_lower:
#             fieldtype = "Currency"
#             width = 150
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             value = row[idx]

#             if "/" in col and value:
#                 value = str(value).strip().replace("₹", "")
#                 parts = [p.strip() for p in re.split(r"\s+", value) if p.strip()]
#                 if len(parts) >= 3:
#                     qty, rate, amount = parts[:3]
#                     html_value = f"""
#                     <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                         <span style='text-align:right;min-width:80px;display:inline-block;'>{qty}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {rate}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {amount}</span>
#                     </div>
#                     """
#                     value = html_value.strip()

#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return columns, data


# # -------------------------------
# # SECOND REPORT (Summary Table)
# # -------------------------------
# def get_summary_rows(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     query = """
#         SELECT
#             si.customer_group AS customer_group,
#             SUM(si.total_qty) AS total_qty,
#             SUM(si.base_net_total / NULLIF(si.total_qty, 0)) AS avg_rate,
#             SUM(si.grand_total) AS total_amount
#         FROM `tabSales Invoice` si
#         WHERE si.docstatus = 1
#           AND si.posting_date BETWEEN %s AND %s
#         GROUP BY si.customer_group
#     """
#     results = frappe.db.sql(query, (from_date, to_date), as_dict=True)

#     summary_data = []
#     for r in results:
#         html_value = f"""
#         <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#             <span style='text-align:right;min-width:80px;display:inline-block;'>{round(r.total_qty or 0, 2)}</span>
#             <span style='margin:0 8px;'>|</span>
#             <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {round(r.avg_rate or 0, 2)}</span>
#             <span style='margin:0 8px;'>|</span>
#             <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {round(r.total_amount or 0, 2)}</span>
#         </div>
#         """

#         summary_data.append({
#             "company": "",
#             "customer": "",
#             "customer_name": "",
#             "customer_group": f"<b>{r.customer_group}</b>",
#             "oct_25": html_value.strip(),
#             "total_amount": f"₹ {round(r.total_amount or 0, 2)}"
#         })

#     return summary_data


# # -------------------------------
# # STORED PROCEDURE CALL
# # -------------------------------
# def call_stored_procedure(from_date, to_date):
#     query = "CALL sp_get_sales_invoice_data(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames





# perfect


# import frappe
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     # 1️⃣ Get main report data
#     columns, data_main = get_data_and_columns(filters)

#     # 2️⃣ Get month-wise summary table
#     data_summary = get_summary_rows(filters, columns)

#     # 3️⃣ Add separator row
#     separator_row = {
#         columns[0]["fieldname"]: "<div style='font-weight:bold;font-size:14px;'>Summary Report</div>"
#     }

#     # Combine both
#     final_data = data_main + [separator_row] + data_summary
#     return columns, final_data


# # -------------------------------
# # MAIN REPORT (Stored Procedure)
# # -------------------------------
# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     results, colnames = call_stored_procedure(from_date, to_date)
#     if not results:
#         return [], []

#     columns = []
#     for col in colnames:
#         col_lower = col.lower()
#         is_month_col = "/" in col

#         if is_month_col:
#             fieldtype = "HTML"
#             width = 300
#         elif "amount" in col_lower or "total" in col_lower:
#             fieldtype = "Currency"
#             width = 150
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             value = row[idx]

#             if "/" in col and value:
#                 value = str(value).strip().replace("₹", "")
#                 parts = [p.strip() for p in re.split(r"\s+", value) if p.strip()]
#                 if len(parts) >= 3:
#                     qty, rate, amount = parts[:3]
#                     html_value = f"""
#                     <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                         <span style='text-align:right;min-width:80px;display:inline-block;'>{qty}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {rate}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {amount}</span>
#                     </div>
#                     """
#                     value = html_value.strip()

#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return columns, data


# # -------------------------------
# # SECOND REPORT (Monthly Summary)
# # -------------------------------
# def get_summary_rows(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     # ✅ ESCAPE %b/%y to avoid Python f-string issues
#     query = """
#         SELECT
#             si.customer_group AS customer_group,
#             DATE_FORMAT(si.posting_date, '%%b/%%y') AS month_year,
#             SUM(si.total_qty) AS total_qty,
#             SUM(si.base_net_total / NULLIF(si.total_qty, 0)) AS avg_rate,
#             SUM(si.grand_total) AS total_amount
#         FROM `tabSales Invoice` si
#         WHERE si.docstatus = 1
#           AND si.posting_date BETWEEN %s AND %s
#         GROUP BY si.customer_group, month_year
#         ORDER BY si.customer_group, MIN(si.posting_date)
#     """
#     results = frappe.db.sql(query, (from_date, to_date), as_dict=True)

#     # Group by customer_group and month
#     summary_map = {}
#     for r in results:
#         grp = r.customer_group
#         month = r.month_year
#         if grp not in summary_map:
#             summary_map[grp] = {}
#         if month not in summary_map[grp]:
#             summary_map[grp][month] = {"qty": 0, "rate": 0, "amount": 0}

#         summary_map[grp][month]["qty"] += r.total_qty or 0
#         summary_map[grp][month]["rate"] += r.avg_rate or 0
#         summary_map[grp][month]["amount"] += r.total_amount or 0

#     # Create summary rows dynamically for each month column
#     summary_data = []
#     month_cols = [col for col in columns if "/" in col["label"]]

#     for grp, months in summary_map.items():
#         row = {
#             "company": "",
#             "customer": "",
#             "customer_name": "",
#             "customer_group": f"<b>{grp}</b>",
#         }

#         for col in month_cols:
#             month_key = col["label"]
#             month_data = months.get(month_key, {"qty": 0, "rate": 0, "amount": 0})
#             html_value = f"""
#             <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                 <span style='text-align:right;min-width:80px;display:inline-block;'>{round(month_data["qty"], 2)}</span>
#                 <span style='margin:0 8px;'>|</span>
#                 <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {round(month_data["rate"], 2)}</span>
#                 <span style='margin:0 8px;'>|</span>
#                 <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {round(month_data["amount"], 2)}</span>
#             </div>
#             """
#             row[col["fieldname"]] = html_value.strip()

#         # Add total column if exists
#         row["total_amount"] = f"₹ {round(sum(m['amount'] for m in months.values()), 2)}"
#         summary_data.append(row)

#     return summary_data


# # -------------------------------
# # STORED PROCEDURE CALL
# # -------------------------------
# def call_stored_procedure(from_date, to_date):
#     query = "CALL sp_get_sales_invoice_data(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames






# import frappe
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     # 1️⃣ Get main report data
#     columns, data_main = get_data_and_columns(filters)

#     # 2️⃣ Get month-wise summary table
#     data_summary = get_summary_rows(filters, columns)

#     # 3️⃣ Add separator row
#     separator_row = {
#         columns[0]["fieldname"]: "<div style='font-weight:bold;font-size:14px;'>Summary Report</div>"
#     }

#     # Combine both
#     final_data = data_main + [separator_row] + data_summary
#     return columns, final_data


# # -------------------------------
# # MAIN REPORT (Stored Procedure)
# # -------------------------------
# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     results, colnames = call_stored_procedure(from_date, to_date)
#     if not results:
#         return [], []

#     columns = []
#     for col in colnames:
#         col_lower = col.lower()
#         is_month_col = "/" in col

#         if is_month_col:
#             fieldtype = "HTML"
#             width = 300
#         elif "amount" in col_lower or "total" in col_lower:
#             fieldtype = "Currency"
#             width = 150
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             value = row[idx]

#             if "/" in col and value:
#                 value = str(value).strip().replace("₹", "")
#                 parts = [p.strip() for p in re.split(r"\s+", value) if p.strip()]
#                 if len(parts) >= 3:
#                     qty, rate, amount = parts[:3]
#                     html_value = f"""
#                     <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                         <span style='text-align:right;min-width:80px;display:inline-block;'>{qty}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {rate}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {amount}</span>
#                     </div>
#                     """
#                     value = html_value.strip()

#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return columns, data


# # -------------------------------
# # SECOND REPORT (Monthly Summary)
# # -------------------------------
# def get_summary_rows(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     # ✅ Use base_net_total for monthly totals (instead of grand_total)
#     query = """
#         SELECT
#             si.customer_group AS customer_group,
#             DATE_FORMAT(si.posting_date, '%%b/%%y') AS month_year,
#             SUM(si.total_qty) AS total_qty,
#             SUM(si.base_net_total / NULLIF(si.total_qty, 0)) AS avg_rate,
#             SUM(si.base_net_total) AS base_amount,     -- month total (base)
#             SUM(si.grand_total) AS total_amount        -- overall total (for last column)
#         FROM `tabSales Invoice` si
#         WHERE si.docstatus = 1
#           AND si.posting_date BETWEEN %s AND %s
#         GROUP BY si.customer_group, month_year
#         ORDER BY si.customer_group, MIN(si.posting_date)
#     """
#     results = frappe.db.sql(query, (from_date, to_date), as_dict=True)

#     # Group by customer_group and month
#     summary_map = {}
#     for r in results:
#         grp = r.customer_group
#         month = r.month_year
#         if grp not in summary_map:
#             summary_map[grp] = {}
#         if month not in summary_map[grp]:
#             summary_map[grp][month] = {"qty": 0, "rate": 0, "base": 0, "total": 0}

#         summary_map[grp][month]["qty"] += r.total_qty or 0
#         summary_map[grp][month]["rate"] += r.avg_rate or 0
#         summary_map[grp][month]["base"] += r.base_amount or 0
#         summary_map[grp][month]["total"] += r.total_amount or 0

#     # Create summary rows dynamically for each month column
#     summary_data = []
#     month_cols = [col for col in columns if "/" in col["label"]]

#     for grp, months in summary_map.items():
#         row = {
#             "company": "",
#             "customer": "",
#             "customer_name": "",
#             "customer_group": f"<b>{grp}</b>",
#         }

#         # Month-wise display using base_amount
#         for col in month_cols:
#             month_key = col["label"]
#             month_data = months.get(month_key, {"qty": 0, "rate": 0, "base": 0})
#             html_value = f"""
#             <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                 <span style='text-align:right;min-width:80px;display:inline-block;'>{round(month_data["qty"], 2)}</span>
#                 <span style='margin:0 8px;'>|</span>
#                 <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {round(month_data["rate"], 2)}</span>
#                 <span style='margin:0 8px;'>|</span>
#                 <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {round(month_data["base"], 2)}</span>
#             </div>
#             """
#             row[col["fieldname"]] = html_value.strip()

#         # ✅ Final total column uses total_amount (not base)
#         total_sum = sum(m["total"] for m in months.values())
#         row["total_amount"] = f"₹ {round(total_sum, 2)}"

#         summary_data.append(row)

#     return summary_data


# # -------------------------------
# # STORED PROCEDURE CALL
# # -------------------------------
# def call_stored_procedure(from_date, to_date):
#     query = "CALL sp_get_sales_invoice_data(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames
















# import frappe
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     # 1️⃣ Get main report data
#     columns, data_main = get_data_and_columns(filters)

#     # 2️⃣ Get summary data (via stored procedure)
#     data_summary = get_summary_data(filters, columns)

#     # 3️⃣ Add separator row
#     separator_row = {
#         columns[0]["fieldname"]: "<div style='font-weight:bold;font-size:14px;'>Summary Report</div>"
#     }

#     # 4️⃣ Combine both
#     final_data = data_main + [separator_row] + data_summary
#     return columns, final_data


# # -------------------------------
# # MAIN REPORT (Stored Procedure)
# # -------------------------------
# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_data", from_date, to_date)
#     if not results:
#         return [], []

#     columns = []
#     for col in colnames:
#         col_lower = col.lower()
#         is_month_col = "/" in col

#         if is_month_col:
#             fieldtype = "HTML"
#             width = 300
#         elif "amount" in col_lower or "total" in col_lower:
#             fieldtype = "Currency"
#             width = 150
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             value = row[idx]

#             # For month columns (Qty | Rate | Amount)
#             if "/" in col and value:
#                 value = str(value).strip().replace("₹", "")
#                 parts = [p.strip() for p in re.split(r"\s+", value) if p.strip()]
#                 if len(parts) >= 3:
#                     qty, rate, amount = parts[:3]
#                     html_value = f"""
#                     <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                         <span style='text-align:right;min-width:80px;display:inline-block;'>{qty}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {rate}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {amount}</span>
#                     </div>
#                     """
#                     value = html_value.strip()

#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return columns, data


# # -------------------------------
# # SUMMARY REPORT (Stored Procedure)
# # -------------------------------
# def get_summary_data(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_summary", from_date, to_date)
#     if not results:
#         return []

#     # Map result to column names
#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             row_dict[fieldname] = row[idx]
#         data.append(row_dict)

#     return data


# # -------------------------------
# # GENERIC STORED PROCEDURE CALL
# # -------------------------------
# def call_stored_procedure(proc_name, from_date, to_date):
#     query = f"CALL {proc_name}(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     # Consume remaining result sets (MySQL quirk)
#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames



# working code

# import frappe 
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     # 1️⃣ Get main report data
#     columns, data_main = get_data_and_columns(filters)

#     # 2️⃣ Get summary data (via stored procedure)
#     data_summary = get_summary_data(filters, columns)

#     # 3️⃣ Add enhanced separator row (with dynamic month + Total Amount)
#     separator_row = build_summary_header_row(columns)

#     # 4️⃣ Combine both
#     final_data = data_main + [separator_row] + data_summary
#     return columns, final_data


# # -------------------------------
# # 🔹 Summary Header Row Builder
# # -------------------------------
# def build_summary_header_row(columns):
#     # """
#     # Builds a header row that shows:
#     # - 'Summary Report' and 'Customer Group' in bold
#     # - Dynamic month column labels (like Oct/25, Nov/25, etc.)
#     # - Bold 'Total Amount'
#     # """
#     separator_row = {}

#     # Summary title and customer group
#     separator_row[columns[0]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Summary Report</div>"
#     separator_row[columns[3]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Customer Group</div>"

#     # Dynamic month headers
#     for col in columns:
#         if "/" in col["label"]:  # month columns
#             separator_row[col["fieldname"]] = f"<div style='font-weight:bold;font-size:14px;text-align:center;'>{col['label']}</div>"

#     # Bold Total Amount header (last column)
#     last_col = columns[-1]
#     separator_row[last_col["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Total Amount</div>"

#     return separator_row


# # -------------------------------
# # MAIN REPORT (Stored Procedure)
# # -------------------------------
# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_data", from_date, to_date)
#     if not results:
#         return [], []

#     columns = []
#     for idx, col in enumerate(colnames):
#         col_lower = col.lower()
#         is_month_col = "/" in col
#         is_last_col = (idx == len(colnames) - 1)  # Check if it's the last column

#         if is_month_col:
#             fieldtype = "HTML"
#             width = 300
#         elif is_last_col and ("amount" in col_lower or "total" in col_lower):
#             # Last column (Total Amount) should be HTML to support bold formatting
#             fieldtype = "HTML"
#             width = 150
#         elif "amount" in col_lower or "total" in col_lower:
#             fieldtype = "Currency"
#             width = 150
#         else:
#             fieldtype = "Data"
#             width = 150

#         columns.append({
#             "label": col.replace("_", " ").title(),
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             value = row[idx]

#             # Format month columns as Qty | Rate | Amount
#             if "/" in col and value:
#                 value = str(value).strip().replace("₹", "")
#                 parts = [p.strip() for p in re.split(r"\s+", value) if p.strip()]
#                 if len(parts) >= 3:
#                     qty, rate, amount = parts[:3]
#                     html_value = f"""
#                     <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                         <span style='text-align:right;min-width:80px;display:inline-block;'>{qty}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {rate}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {amount}</span>
#                     </div>
#                     """
#                     value = html_value.strip()

#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return columns, data


# # -------------------------------
# # SUMMARY REPORT (Stored Procedure)
# # -------------------------------
# def get_summary_data(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_summary", from_date, to_date)
#     if not results:
#         return []

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")
#             value = row[idx]

#             # Apply same HTML style for month columns (Qty | Rate | Amount)
#             if "/" in col and value:
#                 value = str(value).strip().replace("₹", "")
#                 parts = [p.strip() for p in re.split(r"\s+", value) if p.strip()]
#                 if len(parts) >= 3:
#                     qty, rate, amount = parts[:3]
#                     html_value = f"""
#                     <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#                         <span style='text-align:right;min-width:80px;display:inline-block;'>{qty}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {rate}</span>
#                         <span style='margin:0 8px;'>|</span>
#                         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {amount}</span>
#                     </div>
#                     """
#                     value = html_value.strip()

#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return data


# # -------------------------------
# # GENERIC STORED PROCEDURE CALL
# # -------------------------------
# def call_stored_procedure(proc_name, from_date, to_date):
#     query = f"CALL {proc_name}(%s, %s)"
#     params = (from_date, to_date)

#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()

#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []

#     # Consume remaining result sets (MySQL quirk)
#     while cursor.nextset():
#         pass

#     cursor.close()
#     conn.close()

#     return results, colnames
    


# add companywise summary



# import frappe
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     # 1️⃣ Get main report data
#     columns, data_main = get_data_and_columns(filters)

#     # 2️⃣ Get customer-group summary
#     data_summary = get_summary_data(filters, columns)

#     # 3️⃣ Get company-wise summary
#     data_company = get_company_summary_data(filters, columns)

#     # 4️⃣ Build separator rows
#     separator_row_summary = build_summary_header_row(columns)
#     separator_row_company = build_company_header_row(columns)

#     # 5️⃣ Combine all sections
#     final_data = (
#         data_main
#         + [separator_row_summary]
#         + data_summary
#         + [separator_row_company]
#         + data_company
#     )

#     return columns, final_data


# # ======================================================
# # 🔹 HEADER BUILDERS
# # ======================================================

# def build_summary_header_row(columns):
#     separator_row = {}
#     separator_row[columns[0]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Customer Group Summary</div>"

#     for col in columns:
#         if "/" in col["label"]:
#             separator_row[col["fieldname"]] = f"<div style='font-weight:bold;font-size:14px;text-align:center;'>{col['label']}</div>"

#     separator_row[columns[-1]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Total Amount</div>"
#     return separator_row


# def build_company_header_row(columns):
#     separator_row = {}
#     separator_row[columns[0]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Company-wise Summary</div>"

#     for col in columns:
#         if "/" in col["label"]:
#             separator_row[col["fieldname"]] = f"<div style='font-weight:bold;font-size:14px;text-align:center;'>{col['label']}</div>"

#     separator_row[columns[-1]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Total Amount</div>"
#     return separator_row


# # ======================================================
# # 🔹 MAIN REPORT
# # ======================================================
# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")
#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_data", from_date, to_date)
#     if not results:
#         return [], []

#     columns = []
#     for idx, col in enumerate(colnames):
#         col_lower = col.lower()
#         is_month_col = "/" in col
#         is_last_col = idx == len(colnames) - 1

#         fieldtype = "HTML" if is_month_col or (is_last_col and "amount" in col_lower) else "Data"
#         width = 300 if is_month_col else 150

#         columns.append({
#             "label": col,
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             value = row[idx]
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")

#             if "/" in col and value:
#                 value = format_month_value(value)
#             elif idx == len(colnames) - 1 and value:
#                 value = f"<div style='text-align:right;'>₹ {format_number(value)}</div>"

#             row_dict[fieldname] = value
#         data.append(row_dict)

#     return columns, data


# # ======================================================
# # 🔹 CUSTOMER GROUP SUMMARY
# # ======================================================
# def get_summary_data(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_summary", from_date, to_date)
#     if not results:
#         return []

#     return build_summary_rows(results, colnames)


# # ======================================================
# # 🔹 COMPANY-WISE SUMMARY
# # ======================================================
# def get_company_summary_data(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_company_summary", from_date, to_date)
#     if not results:
#         return []

#     return build_summary_rows(results, colnames)


# # ======================================================
# # 🔹 COMMON SUMMARY FORMATTER
# # ======================================================
# def build_summary_rows(results, colnames):
#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             value = row[idx]
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")

#             if "/" in col and value:
#                 value = format_month_value(value)
#             elif idx == len(colnames) - 1 and value:
#                 value = f"<div style='text-align:right;'>₹ {format_number(value)}</div>"

#             row_dict[fieldname] = value
#         data.append(row_dict)
#     return data


# # ======================================================
# # 🔹 FORMATTER FOR MONTH COLUMNS
# # ======================================================
# def format_month_value(value):
#     if not value:
#         return "<div style='text-align:center;'>-</div>"

#     value = str(value).replace("₹", "").replace(",", "").strip()
#     parts = re.split(r"[|, ]+", value)
#     parts = [p.strip() for p in parts if p.strip()]

#     qty = format_number(parts[0]) if len(parts) > 0 else "0.00"
#     rate = format_number(parts[1]) if len(parts) > 1 else "0.00"
#     amount = format_number(parts[2]) if len(parts) > 2 else "0.00"

#     return f"""
#     <div style='display:flex;align-items:center;font-family:monospace;font-size:13px;'>
#         <span style='text-align:right;min-width:80px;display:inline-block;'>{qty}</span>
#         <span style='margin:0 6px;'>|</span>
#         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {rate}</span>
#         <span style='margin:0 6px;'>|</span>
#         <span style='text-align:right;min-width:90px;display:inline-block;'>₹ {amount}</span>
#     </div>
#     """.strip()


# # ======================================================
# # 🔹 HELPER: FORMAT NUMBER
# # ======================================================
# def format_number(num):
#     try:
#         return f"{float(num):,.2f}"
#     except:
#         return str(num)


# # ======================================================
# # 🔹 GENERIC STORED PROCEDURE CALL
# # ======================================================
# def call_stored_procedure(proc_name, from_date, to_date):
#     query = f"CALL {proc_name}(%s, %s)"
#     params = (from_date, to_date)
#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()
#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     colnames = [desc[0] for desc in cursor.description] if cursor.description else []
#     while cursor.nextset():
#         pass
#     cursor.close()
#     conn.close()
#     return results, colnames








# import frappe
# import re

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     # 1️⃣ Get main report data
#     columns, data_main = get_data_and_columns(filters)

#     # 2️⃣ Get customer-group summary
#     data_summary = get_summary_data(filters, columns)

#     # 3️⃣ Get company-wise summary
#     data_company = get_company_summary_data(filters, columns)

#     # 4️⃣ Build separator rows
#     separator_row_summary = build_summary_header_row(columns)
#     separator_row_company = build_company_header_row(columns)

#     # 5️⃣ Combine all sections
#     final_data = (
#         data_main
#         + [separator_row_summary]
#         + data_summary
#         + [separator_row_company]
#         + data_company
#     )

#     return columns, final_data


# # ======================================================
# # 🔹 HEADER BUILDERS
# # ======================================================
# def build_summary_header_row(columns):
#     row = {}
#     row[columns[0]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Customer Group Summary</div>"
#     for col in columns:
#         if "/" in col["label"]:
#             row[col["fieldname"]] = f"<div style='font-weight:bold;font-size:14px;text-align:center;'>{col['label']}</div>"
#     row[columns[-1]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Total Amount</div>"
#     return row


# def build_company_header_row(columns):
#     row = {}
#     row[columns[0]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Company-wise Summary</div>"
#     for col in columns:
#         if "/" in col["label"]:
#             row[col["fieldname"]] = f"<div style='font-weight:bold;font-size:14px;text-align:center;'>{col['label']}</div>"
#     row[columns[-1]["fieldname"]] = "<div style='font-weight:bold;font-size:14px;'>Total Amount</div>"
#     return row


# # ======================================================
# # 🔹 MAIN REPORT DATA
# # ======================================================
# def get_data_and_columns(filters):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")
#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_data", from_date, to_date)
#     if not results:
#         return [], []

#     columns = []
#     for idx, col in enumerate(colnames):
#         col_lower = col.lower()
#         is_month_col = "/" in col
#         is_amount_col = "amount" in col_lower
#         fieldtype = "HTML" if is_month_col or is_amount_col else "Data"
#         width = 200 if is_month_col else 150

#         columns.append({
#             "label": col,
#             "fieldname": col_lower.replace(" ", "_").replace("/", "_"),
#             "fieldtype": fieldtype,
#             "width": width
#         })

#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             val = row[idx]
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")

#             if "/" in col:
#                 val = format_month_value(val)
#             elif idx == len(colnames) - 1 and val:
#                 val = f"<div style='text-align:right;'>₹ {format_number(val)}</div>"

#             row_dict[fieldname] = val
#         data.append(row_dict)

#     return columns, data


# # ======================================================
# # 🔹 SUMMARY + COMPANY SUMMARY
# # ======================================================
# def get_summary_data(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_summary", from_date, to_date)
#     return build_summary_rows(results, colnames)


# def get_company_summary_data(filters, columns):
#     from_date = filters.get("from_date")
#     to_date = filters.get("to_date")

#     results, colnames = call_stored_procedure("sp_get_sales_invoice_company_summary", from_date, to_date)
#     return build_summary_rows(results, colnames)


# def build_summary_rows(results, colnames):
#     data = []
#     for row in results:
#         row_dict = {}
#         for idx, col in enumerate(colnames):
#             val = row[idx]
#             fieldname = col.lower().replace(" ", "_").replace("/", "_")

#             if "/" in col:
#                 val = format_month_value(val)
#             elif idx == len(colnames) - 1 and val:
#                 val = f"<div style='text-align:right;'>₹ {format_number(val)}</div>"

#             row_dict[fieldname] = val
#         data.append(row_dict)
#     return data


# # ======================================================
# # 🔹 INLINE MONTH FORMATTER (Q | R | A with ₹)
# # ======================================================
# def format_month_value(value):
#     if not value:
#         return "<div style='text-align:center;'>-</div>"

#     value = str(value).replace("₹", "").replace(",", "").strip()
#     parts = re.split(r"[|, ]+", value)
#     parts = [p.strip() for p in parts if p.strip()]

#     qty = format_number(parts[0]) if len(parts) > 0 else "0.00"
#     rate = format_number(parts[1]) if len(parts) > 1 else "0.00"
#     amount = format_number(parts[2]) if len(parts) > 2 else "0.00"

#     # 💡 Inline style with ₹ sign before Rate and Amount
#     return f"""
#     <div style='text-align:center;font-family:monospace;font-size:13px;'>
#         Q: {qty} | R: ₹ {rate} | A: ₹ {amount}
#     </div>
#     """.strip()


# # ======================================================
# # 🔹 HELPER: FORMAT NUMBER
# # ======================================================
# def format_number(num):
#     try:
#         return f"{float(num):,.2f}"
#     except:
#         return str(num)


# # ======================================================
# # 🔹 DB CALL
# # ======================================================
# def call_stored_procedure(proc_name, from_date, to_date):
#     query = f"CALL {proc_name}(%s, %s)"
#     conn = frappe.db.get_connection()
#     cursor = conn.cursor()
#     cursor.execute(query, (from_date, to_date))
#     results = cursor.fetchall()
#     colnames = [d[0] for d in cursor.description] if cursor.description else []
#     while cursor.nextset():
#         pass
#     cursor.close()
#     conn.close()
#     return results, colnames






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
