import frappe

def update_item_fields(doc, method):
    """
    Auto-update item_code, item_name, description, and barcode
    when Item is saved.
    """
    parts = []

    # Add item_name only if no parameters
    if doc.item_name and not doc.custom_item_parameters:
        parts.append(doc.item_name.strip().upper())

    # Add custom parameters
    for row in doc.custom_item_parameters or []:
        if row.value:
            try:
                # Try to fetch actual name from MiscellaneousMst
                linked_doc = frappe.get_doc("MiscellaneousMst", row.value)
                parts.append(linked_doc.value.strip().upper())
            except:
                # Fallback to ID if not found
                parts.append(row.value.strip().upper())

    new_code = "-".join(parts)

    if not new_code:
        return

    if doc.custom_item_parameters:
        # Parameters exist → auto set
        doc.item_code = new_code
        doc.item_name = new_code
        doc.description = new_code
    else:
        # No parameters → only description sync
        doc.description = new_code or doc.item_name or doc.item_code

    # ✅ Auto-fill Barcode
    if doc.barcodes and len(doc.barcodes) > 0:
        doc.barcodes[0].barcode = new_code


def rename_item_after_save(doc, method):
    """
    Rename Item after insert/update to avoid 404 issue.
    """
    parts = []

    if doc.item_name and not doc.custom_item_parameters:
        parts.append(doc.item_name.strip().upper())

    for row in doc.custom_item_parameters or []:
        if row.value:
            try:
                # Try to fetch actual name from MiscellaneousMst
                linked_doc = frappe.get_doc("MiscellaneousMst", row.value)
                parts.append(linked_doc.value.strip().upper())
            except:
                # Fallback to ID if not found
                parts.append(row.value.strip().upper())

    new_code = "-".join(parts)
    if not new_code or doc.name == new_code:
        return

    old_name = doc.name

    frappe.enqueue("frappe.model.rename_doc.rename_doc", 
                   doctype="Item", 
                   old=old_name, 
                   new=new_code, 
                   force=True, 
                   merge=False)

    # Update Item Parameter table if needed
    frappe.db.sql("""
        UPDATE `tabItem Parameter`
        SET parent = %s
        WHERE parent = %s
    """, (new_code, old_name))








