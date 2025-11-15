// frappe.provide("frappe.ui.form");

// (function() {
//     // Save the original function so we don't lose Frappe behavior
//     const original_setup_visible_columns = frappe.ui.form.Grid.prototype.setup_visible_columns;

//     frappe.ui.form.Grid.prototype.setup_visible_columns = function() {
//         // Call the original function
//         original_setup_visible_columns.call(this);

//         // Then override the column width validation logic
//         let total_width = 0;
//         if (this.visible_columns && this.visible_columns.length) {
//             total_width = this.visible_columns.reduce((total, col) => {
//                 return total + (col[1].width || 1);
//             }, 0);
//         }

//         // ✅ Change the limit or disable it
//         const max_allowed_width = 30; // you can increase this value as needed

//         if (total_width > max_allowed_width) {
//             console.warn(
//                 `⚠️ Column width (${total_width}) exceeds ${max_allowed_width}, but override allows it.`
//             );
//         }
//     };
// })();




frappe.provide("frappe.ui.form");

(function() {
    // Override the Frappe Grid setup completely
    const original_fn = frappe.ui.form.Grid.prototype.setup_visible_columns;

    frappe.ui.form.Grid.prototype.setup_visible_columns = function() {
        original_fn.call(this);

        // Bypass the column width check entirely
        try {
            if (this.visible_columns) {
                let total_width = this.visible_columns.reduce((total, col) => {
                    return total + (col[1].width || 1);
                }, 0);

                // ✅ Ignore the width limit — no restriction at all
                if (total_width > 10) {
                    console.info(
                        `%c[GalaxyNext Override]%c Ignored column width limit (${total_width})`,
                        "color: #4CAF50; font-weight: bold;",
                        "color: inherit;"
                    );
                }
            }
        } catch (e) {
            console.warn("Grid column override failed:", e);
        }
    };

    // Disable the actual validation check (this is key)
    frappe.ui.form.GridRow.prototype.validate_columns = function() {
        // Do nothing (bypass Frappe's check)
        return true;
    };

    // Disable frappe.throw() for this specific validation message
    const original_throw = frappe.throw;
    frappe.throw = function(message, title) {
        if (
            typeof message === "string" &&
            message.includes("The total column width cannot be more than 10")
        ) {
            console.warn("[GalaxyNext Override] Ignored column width validation");
            return; // prevent showing error popup
        }
        return original_throw.call(this, message, title);
    };
})();
