// frappe.query_reports["Production Plan Report"] = {
//     "filters": [
//         {
//             "fieldname": "company",
//             "label": "Company",
//             "fieldtype": "Link",
//             "options": "Company",
//             "default": frappe.defaults.get_user_default("Company"),
//             "reqd": 1
//         },
//         {
//             "fieldname": "production_plan",
//             "label": "Production Plan",
//             "fieldtype": "Link",
//             "options": "Production Plan",
//             "get_query": function() {
//                 const company = frappe.query_report.get_filter_value('company');
//                 if (company) {
//                     return {
//                         "filters": { "company": company }
//                     };
//                 }
//             }
//         }
//     ]
// };



// working


// frappe.query_reports["Production Plan Report"] = {
//     "filters": [
//         {
//             "fieldname": "company",
//             "label": __("Company"),
//             "fieldtype": "Link",
//             "options": "Company",
//             "reqd": 1,
//             "default": frappe.defaults.get_user_default("Company")
//         },
//         {
//             "fieldname": "production_plan",
//             "label": __("Production Plan"),
//             "fieldtype": "Link",
//             "options": "Production Plan",
//             "get_query": function() {
//                 const company = frappe.query_report.get_filter_value('company');
//                 if (company) {
//                     return {
//                         filters: {
//                             "company": company
//                         }
//                     };
//                 } else {
//                     return {};
//                 }
//             }
//         }
//     ]
// };



frappe.query_reports["Production Plan Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1,
            "default": frappe.defaults.get_user_default("Company")
        },
        {
            "fieldname": "production_plan",
            "label": __("Production Plan"),
            "fieldtype": "Link",
            "options": "Production Plan",
            "get_query": function() {
                const company = frappe.query_report.get_filter_value('company');
                if (company) {
                    return {
                        filters: { "company": company }
                    };
                } else {
                    return {};
                }
            }
        }
    ]
};
