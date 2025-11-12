# import frappe
# import json

# @frappe.whitelist()
# def get_workorders():
#     """Fetch Work Orders with workstation from Work Order Operation child table"""
#     work_orders = frappe.db.sql("""
#         SELECT
#             wo.name,
#             wo.production_item,
#             wo.planned_start_date,
#             wo.planned_end_date,
#             wop.workstation
#         FROM
#             `tabWork Order` AS wo
#         LEFT JOIN
#             `tabWork Order Operation` AS wop
#         ON
#             wop.parent = wo.name
#         WHERE
#             wo.status NOT IN ('Completed', 'Cancelled')
#         GROUP BY
#             wo.name
#         ORDER BY
#             wo.planned_start_date ASC
#     """, as_dict=True)

#     return work_orders


# @frappe.whitelist()
# def update_workorder(work_order_id, data):
#     """Update planned dates or workstation for a Work Order."""
#     if isinstance(data, str):
#         data = json.loads(data)

#     wo = frappe.get_doc("Work Order", work_order_id)
#     if "planned_start_date" in data:
#         wo.planned_start_date = data["planned_start_date"]
#     if "planned_end_date" in data:
#         wo.planned_end_date = data["planned_end_date"]
#     wo.save(ignore_permissions=True)

#     if "workstation" in data:
#         operations = frappe.get_all("Work Order Operation", filters={"parent": work_order_id})
#         for op in operations:
#             frappe.db.set_value("Work Order Operation", op.name, "workstation", data["workstation"])
#         frappe.db.commit()

#     return {"status": "success"}



# import frappe
# import json
# from frappe.utils import now_datetime, get_datetime

# @frappe.whitelist()
# def get_workorders(workstation=None):
#     """Fetch Work Orders with workstation from Work Order Operation child table"""
    
#     conditions = "wo.status NOT IN ('Completed', 'Cancelled') AND wo.docstatus < 2"
    
#     if workstation:
#         conditions += f" AND wop.workstation = '{workstation}'"
    
#     work_orders = frappe.db.sql(f"""
#         SELECT
#             wo.name,
#             wo.production_item,
#             wo.planned_start_date,
#             wo.planned_end_date,
#             wo.status,
#             wop.workstation
#         FROM
#             `tabWork Order` AS wo
#         LEFT JOIN
#             `tabWork Order Operation` AS wop
#         ON
#             wop.parent = wo.name
#         WHERE
#             {conditions}
#         GROUP BY
#             wo.name
#         ORDER BY
#             wo.planned_start_date ASC
#     """, as_dict=True)
    
#     return work_orders

# @frappe.whitelist()
# def update_workorder(work_order_id, data):
#     """Update planned dates or workstation for a Work Order with proper activity tracking."""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         # Get work order document
#         wo = frappe.get_doc("Work Order", work_order_id)
        
#         # Store old values for activity tracking
#         old_start = wo.planned_start_date
#         old_end = wo.planned_end_date
#         old_workstation = None
        
#         # Get current workstation
#         if wo.operations:
#             old_workstation = wo.operations[0].workstation if wo.operations else None
        
#         changes_made = []
        
#         # Update planned dates
#         if "planned_start_date" in data and data["planned_start_date"]:
#             new_start = get_datetime(data["planned_start_date"])
#             if old_start != new_start:
#                 wo.planned_start_date = new_start
#                 changes_made.append(f"Planned Start Date changed from {old_start} to {new_start}")
        
#         if "planned_end_date" in data and data["planned_end_date"]:
#             new_end = get_datetime(data["planned_end_date"])
#             if old_end != new_end:
#                 wo.planned_end_date = new_end
#                 changes_made.append(f"Planned End Date changed from {old_end} to {new_end}")
        
#         # Save work order with changes
#         if changes_made:
#             wo.flags.ignore_validate_update_after_submit = True
#             wo.save(ignore_permissions=True)
#             frappe.db.commit()
        
#         # Update workstation in operations
#         if "workstation" in data and data["workstation"]:
#             new_workstation = data["workstation"]
            
#             if new_workstation != old_workstation:
#                 operations = frappe.get_all(
#                     "Work Order Operation", 
#                     filters={"parent": work_order_id},
#                     fields=["name", "workstation"]
#                 )
                
#                 for op in operations:
#                     frappe.db.set_value(
#                         "Work Order Operation", 
#                         op.name, 
#                         "workstation", 
#                         new_workstation,
#                         update_modified=True
#                     )
                
#                 changes_made.append(f"Workstation changed from {old_workstation or 'Unassigned'} to {new_workstation}")
#                 frappe.db.commit()
        
#         # Add comment to track changes in activity
#         if changes_made:
#             comment_text = "Updated via Gantt View:\n" + "\n".join(changes_made)
            
#             wo.add_comment(
#                 comment_type="Info",
#                 text=comment_text
#             )
            
#             frappe.db.commit()
        
#         return {
#             "status": "success",
#             "message": "Work Order updated successfully",
#             "changes": changes_made
#         }
    
#     except Exception as e:
#         frappe.log_error(f"Error updating work order {work_order_id}: {str(e)}")
#         return {
#             "status": "error",
#             "message": str(e)
#         }






import frappe, json
from frappe.utils import get_datetime

@frappe.whitelist()
def get_workorders(workstation=None):
    conditions = "wo.status NOT IN ('Completed', 'Cancelled') AND wo.docstatus < 2"

    if workstation:
        conditions += f" AND wop.workstation = '{workstation}'"

    work_orders = frappe.db.sql(f"""
        SELECT
            wo.name,
            wo.production_item,
            wo.planned_start_date,
            wo.planned_end_date,
            wo.status,
            IFNULL(wop.workstation, 'Unassigned') AS workstation
        FROM `tabWork Order` wo
        LEFT JOIN `tabWork Order Operation` wop ON wop.parent = wo.name
        WHERE {conditions}
        GROUP BY wo.name
        ORDER BY wo.planned_start_date ASC
    """, as_dict=True)

    return work_orders


@frappe.whitelist()
def update_workorder(work_order_id, data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        wo = frappe.get_doc("Work Order", work_order_id)

        old_start = wo.planned_start_date
        old_end = wo.planned_end_date

        changes_made = []

        if "planned_start_date" in data and data["planned_start_date"]:
            new_start = get_datetime(data["planned_start_date"])
            if old_start != new_start:
                wo.planned_start_date = new_start
                changes_made.append(f"Start: {old_start} → {new_start}")

        if "planned_end_date" in data and data["planned_end_date"]:
            new_end = get_datetime(data["planned_end_date"])
            if old_end != new_end:
                wo.planned_end_date = new_end
                changes_made.append(f"End: {old_end} → {new_end}")

        wo.flags.ignore_validate_update_after_submit = True
        wo.save(ignore_permissions=True)
        frappe.db.commit()

        if "workstation" in data and data["workstation"]:
            new_ws = data["workstation"]
            ops = frappe.get_all("Work Order Operation", filters={"parent": work_order_id})
            for op in ops:
                frappe.db.set_value("Work Order Operation", op.name, "workstation", new_ws)
            frappe.db.commit()
            changes_made.append(f"Workstation updated → {new_ws}")

        if changes_made:
            wo.add_comment("Info", "Updated via Gantt:\n" + "\n".join(changes_made))

        return {"status": "success", "message": "Updated successfully", "changes": changes_made}

    except Exception as e:
        frappe.log_error(f"Error updating work order {work_order_id}: {str(e)}")
        return {"status": "error", "message": str(e)}
