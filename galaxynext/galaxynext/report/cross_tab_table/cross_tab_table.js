// Copyright (c) 2025,contributors
// For license information, please see license.txt

// frappe.query_reports["Cross Tab Table"] = {
// 	"filters": [
// 			{
//             "fieldname": "from_date",
//             "label": "From Date",
//             "fieldtype": "Date",
//             "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
//             "reqd": 1
//         },
//         {
//             "fieldname": "to_date",
//             "label": "To Date",
//             "fieldtype": "Date",
//             "default": frappe.datetime.get_today(),
//             "reqd": 1
//         }
// 	]
// };

// Copyright (c) 2025
// For license information, please see license.txt

frappe.query_reports["Cross Tab Table"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
    ]
};

