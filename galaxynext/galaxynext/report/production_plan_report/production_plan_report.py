# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {
#             "label": _("Company"),
#             "fieldname": "company",
#             "fieldtype": "Link",
#             "options": "Company",
#             "width": 150
#         },
#         {
#             "label": _("Production Plan"),
#             "fieldname": "production_plan",
#             "fieldtype": "Link",
#             "options": "Production Plan",
#             "width": 180
#         },
#         {
#             "label": _("Work Order"),
#             "fieldname": "work_order",
#             "fieldtype": "Link",
#             "options": "Work Order",
#             "width": 180
#         },
#         {
#             "label": _("Item"),
#             "fieldname": "item",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 150
#         },
#         {
#             "label": _("Sales Order"),
#             "fieldname": "sales_order",
#             "fieldtype": "Link",
#             "options": "Sales Order",
#             "width": 150
#         },
#         {
#             "label": _("BOM"),
#             "fieldname": "bom",
#             "fieldtype": "Link",
#             "options": "BOM",
#             "width": 180
#         },
#         {
#             "label": _("WO Status"),
#             "fieldname": "wo_status",
#             "fieldtype": "Data",
#             "width": 120
#         },
#         {
#             "label": _("Operation"),
#             "fieldname": "operation",
#             "fieldtype": "Link",
#             "options": "Operation",
#             "width": 150
#         },
#         {
#             "label": _("Op Status"),
#             "fieldname": "op_status",
#             "fieldtype": "Data",
#             "width": 120
#         },
#         {
#             "label": _("Job Card"),
#             "fieldname": "job_card",
#             "fieldtype": "Link",
#             "options": "Job Card",
#             "width": 180
#         },
#         {
#             "label": _("JC Status"),
#             "fieldname": "jc_status",
#             "fieldtype": "Data",
#             "width": 120
#         },
#         {
#             "label": _("Planned Qty"),
#             "fieldname": "planned_qty",
#             "fieldtype": "Float",
#             "width": 100
#         },
#         {
#             "label": _("Produced Qty"),
#             "fieldname": "produced_qty",
#             "fieldtype": "Float",
#             "width": 100
#         },
#         {
#             "label": _("Pending Qty"),
#             "fieldname": "pending_qty",
#             "fieldtype": "Float",
#             "width": 100
#         }
#     ]


# def get_data(filters):
#     if not filters:
#         filters = {}

#     conditions = get_conditions(filters)

#     query = """
#         SELECT
#             wo.company,
#             wo.production_plan,
#             wo.name AS work_order,
#             wo.production_item AS item,
#             wo.sales_order,
#             wo.bom_no AS bom,
#             wo.`status` AS wo_status,
#             wop.operation,
#             wop.status AS op_status,
#             jc.name AS job_card,
#             jc.status AS jc_status,
#             wo.qty AS planned_qty,
#             wo.produced_qty,
#             (wo.qty - IFNULL(wo.produced_qty, 0)) AS pending_qty
#         FROM `tabWork Order` wo
#         LEFT JOIN `tabWork Order Operation` wop ON wop.parent = wo.name
#         LEFT JOIN `tabJob Card` jc ON jc.work_order = wo.name
#         WHERE wo.docstatus = 1 {conditions}
#         ORDER BY wo.creation DESC, wo.name DESC, wop.idx
#     """.format(conditions=conditions)

#     data = frappe.db.sql(query, filters, as_dict=1)

#     return data if data else []


# def get_conditions(filters):
#     conditions = ""

#     if filters.get("company"):
#         conditions += " AND wo.company = %(company)s"

#     if filters.get("production_plan"):
#         conditions += " AND wo.production_plan = %(production_plan)s"

#     return conditions




# working

# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
# from frappe import _

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
#         {"label": _("Production Plan"), "fieldname": "production_plan", "fieldtype": "Link", "options": "Production Plan", "width": 180},
#         {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 180},
#         {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
#         {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
#         {"label": _("BOM"), "fieldname": "bom", "fieldtype": "Link", "options": "BOM", "width": 180},
#         {"label": _("WO Status"), "fieldname": "wo_status", "fieldtype": "Data", "width": 120},
#         {"label": _("Operations"), "fieldname": "operations", "fieldtype": "Data", "width": 250},
#         {"label": _("Job Cards"), "fieldname": "job_cards", "fieldtype": "Data", "width": 250},
#         {"label": _("Planned Qty"), "fieldname": "planned_qty", "fieldtype": "Float", "width": 100},
#         {"label": _("Produced Qty"), "fieldname": "produced_qty", "fieldtype": "Float", "width": 100},
#         {"label": _("Pending Qty"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 100},
#     ]


# def get_data(filters):
#     if not filters:
#         filters = {}

#     conditions = get_conditions(filters)

#     # main work orders
#     work_orders = frappe.db.sql("""
#         SELECT
#             wo.name AS work_order,
#             wo.company,
#             wo.production_plan,
#             wo.production_item AS item,
#             wo.sales_order,
#             wo.bom_no AS bom,
#             wo.status AS wo_status,
#             wo.qty AS planned_qty,
#             wo.produced_qty,
#             (wo.qty - IFNULL(wo.produced_qty, 0)) AS pending_qty
#         FROM `tabWork Order` wo
#         WHERE wo.docstatus = 1 {conditions}
#         ORDER BY wo.creation DESC
#     """.format(conditions=conditions), filters, as_dict=1)

#     # collect operations & job cards for each work order
#     for wo in work_orders:
#         operations = frappe.db.sql("""
#             SELECT wop.operation, wop.status AS op_status, jc.name AS job_card, jc.status AS jc_status
#             FROM `tabWork Order Operation` wop
#             LEFT JOIN `tabJob Card` jc 
#                 ON jc.work_order = wop.parent AND jc.operation = wop.operation
#             WHERE wop.parent = %s
#             ORDER BY wop.idx
#         """, wo.work_order, as_dict=1)

#         # join all operations + statuses as text
#         wo["operations"] = ", ".join([f"{op.operation} ({op.op_status})" for op in operations]) if operations else ""
#         wo["job_cards"] = ", ".join([f"{op.job_card or ''} ({op.jc_status or ''})" for op in operations if op.job_card]) if operations else ""

#     return work_orders


# def get_conditions(filters):
#     conditions = ""
#     if filters.get("company"):
#         conditions += " AND wo.company = %(company)s"
#     if filters.get("production_plan"):
#         conditions += " AND wo.production_plan = %(production_plan)s"
#     return conditions







import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": _("Production Plan"), "fieldname": "production_plan", "fieldtype": "Link", "options": "Production Plan", "width": 180},
        {"label": _("PP Status"), "fieldname": "pp_status", "fieldtype": "Data", "width": 120},
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 180},
        {"label": _("WO Status"), "fieldname": "wo_status", "fieldtype": "Data", "width": 120},
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
        {"label": _("BOM"), "fieldname": "bom", "fieldtype": "Link", "options": "BOM", "width": 150},
        {"label": _("Operations"), "fieldname": "operations", "fieldtype": "Data", "width": 250},
        {"label": _("Job Cards"), "fieldname": "job_cards", "fieldtype": "Data", "width": 250},
        {"label": _("Planned Qty"), "fieldname": "planned_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Produced Qty"), "fieldname": "produced_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Pending Qty"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 100},
    ]


def get_data(filters):
    if not filters:
        filters = {}

    conditions = get_conditions(filters)

    # include all production plans + related work orders if exist
    records = frappe.db.sql(f"""
        SELECT 
            pp.name AS production_plan,
            pp.company,
            pp.status AS pp_status,
            wo.name AS work_order,
            wo.status AS wo_status,
            wo.production_item AS item,
            wo.sales_order,
            wo.bom_no AS bom,
            wo.qty AS planned_qty,
            wo.produced_qty,
            (wo.qty - IFNULL(wo.produced_qty, 0)) AS pending_qty
        FROM `tabProduction Plan` pp
        LEFT JOIN `tabWork Order` wo ON wo.production_plan = pp.name
        WHERE 1=1 {conditions}
        ORDER BY pp.creation DESC
    """, filters, as_dict=1)

    # collect operation + job card details if available
    for r in records:
        if r.get("work_order"):
            operations = frappe.db.sql("""
                SELECT wop.operation, wop.status AS op_status, jc.name AS job_card, jc.status AS jc_status
                FROM `tabWork Order Operation` wop
                LEFT JOIN `tabJob Card` jc 
                    ON jc.work_order = wop.parent AND jc.operation = wop.operation
                WHERE wop.parent = %s
                ORDER BY wop.idx
            """, r.work_order, as_dict=1)

            r["operations"] = ", ".join([f"{op.operation} ({op.op_status})" for op in operations]) if operations else ""
            r["job_cards"] = ", ".join([f"{op.job_card or ''} ({op.jc_status or ''})" for op in operations if op.job_card]) if operations else ""
        else:
            r["operations"] = ""
            r["job_cards"] = ""

    return records


def get_conditions(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " AND pp.company = %(company)s"
    if filters.get("production_plan"):
        conditions += " AND pp.name = %(production_plan)s"
    return conditions
