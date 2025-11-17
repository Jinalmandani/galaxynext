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