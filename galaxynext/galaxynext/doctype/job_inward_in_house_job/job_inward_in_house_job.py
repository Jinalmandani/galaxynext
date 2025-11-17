# #import frappe
# from frappe.model.document import Document

# class JobInwardInHouseJob(Document):
#     pass



# import frappe
# from frappe.model.document import Document

# class JobInwardInHouseJob(Document):
#     pass


# @frappe.whitelist()
# def get_subcontractor_stock_entries(supplier):
#     # Stock Entry list
#     stock_entries = frappe.get_all(
#         "Stock Entry",
#         filters={"stock_entry_type": "Send to Subcontractor", "supplier": supplier},
#         fields=["name", "posting_date", "posting_time"],
#         ignore_permissions=True
#     )

#     result = []
#     for se in stock_entries:
#         # Stock Entry Detail list
#         items = frappe.get_all(
#             "Stock Entry Detail",
#             filters={"parent": se.name},
#             fields=["item_code", "item_name", "qty", "t_warehouse", "uom", "basic_rate", "parent"],
#             ignore_permissions=True
#         )

#         # Add item_group for each item
#         for item in items:
#             item_group = frappe.db.get_value("Item", item.item_code, "item_group", cache=True)
#             item["item_group"] = item_group or ""

#         result.append({
#             "stock_entry": se,
#             "items": items
#         })

#     return result







import frappe
from frappe.model.document import Document

class JobInwardInHouseJob(Document):
    pass


@frappe.whitelist()
def get_subcontractor_stock_entries(supplier):
    # Stock Entry list (direct custom supplier field)
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={
            "stock_entry_type": "Send to Subcontractor",
            "supplier": supplier,
            "docstatus": 1  # ✅ Only submitted
        },
        fields=["name", "posting_date", "posting_time"],
        ignore_permissions=True
    )

    result = []
    for se in stock_entries:
        # Stock Entry Detail list
        items = frappe.get_all(
            "Stock Entry Detail",
            filters={"parent": se.name},
            fields=["item_code", "item_name", "qty", "t_warehouse",
                    "uom", "basic_rate", "parent"],
            ignore_permissions=True
        )

        # Add item_group for each item
        for item in items:
            item_group = frappe.db.get_value("Item", item.item_code, "item_group", cache=True)
            item["item_group"] = item_group or ""

        result.append({
            "stock_entry": se,
            "items": items
        })

    return result
