# # galaxynext/api.py

# import frappe

# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def get_miscellaneous_options(doctype, txt, searchfield, start, page_len, filters=None):
#     """
#     Returns MiscellaneousMst options filtered by trantype + status=1.
#     """
#     filters = filters or {}
#     trantype = filters.get("trantype")
#     txt = txt or ""

#     if not trantype:
#         return []

#     like_txt = f"%{txt}%"

#     return frappe.db.sql("""
#         SELECT name, value
#         FROM `tabMiscellaneousMst`
#         WHERE trantype = %s
#           AND status = 'true'
#           AND (name LIKE %s OR value LIKE %s)
#         ORDER BY value
#         LIMIT %s, %s
#     """, (trantype, like_txt, like_txt, start, page_len))



# galaxynext/api.py
import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_miscellaneous_options(doctype, txt, searchfield, start, page_len, filters=None):
    """
    Returns MiscellaneousMst options filtered by trantype + status='true'.
    """
    filters = filters or {}
    trantype = filters.get("trantype")
    txt = txt or ""

    if not trantype:
        return []

    like_txt = f"%{txt}%"

    # IMPORTANT: Return as list of tuples (name, value) for ERPNext dropdown
    return frappe.db.sql("""
        SELECT name, value
        FROM `tabMiscellaneousMst`
        WHERE trantype = %s
          AND status = 'true'
          AND (name LIKE %s OR value LIKE %s)
        ORDER BY value
        LIMIT %s, %s
    """, (trantype, like_txt, like_txt, start, page_len), as_list=True)  # ← as_list=True जरूरी है!
    
# -------------------------------------------------------------------------------

# # import frappe
# from frappe.utils import get_datetime

# @frappe.whitelist()
# def get_work_orders(workstation=None, status=None):
#     filters = {"docstatus": ["<", 1]}
#     if workstation:
#         filters["operations.workstation"] = workstation
#     if status:
#         filters["status"] = status

#     work_orders = frappe.get_all(
#         "Work Order",
#         fields=["name", "production_item", "planned_start_date", "planned_end_date", "status"],
#         filters=filters,
#     )

#     tasks = []
#     for wo in work_orders:
#         tasks.append({
#             "id": wo.name,
#             "name": wo.production_item,
#             "start": wo.planned_start_date,
#             "end": wo.planned_end_date,
#             "progress": 100 if wo.status == "Completed" else 50,
#             "workstation": get_workstation_for_wo(wo.name),
#         })
#     return tasks


# def get_workstation_for_wo(wo_name):
#     op = frappe.db.get_value("Work Order Operation", {"parent": wo_name}, "workstation")
#     return op or "Unassigned"


# @frappe.whitelist()
# def update_work_order_dates(name, start_date, end_date):
#     frappe.db.set_value("Work Order", name, {
#         "planned_start_date": get_datetime(start_date),
#         "planned_end_date": get_datetime(end_date)
#     })
#     frappe.db.commit()
#     return {"message": "Updated successfully"}