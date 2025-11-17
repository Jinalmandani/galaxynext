
app_name = "galaxynext"
app_title = "galaxynext"
app_publisher = "khushi"
app_description = "text change"
app_email = "khushim@gmail.com"
app_license = "mit"
    
app_include_js = "/assets/galaxynext/js/custom_about.js"

# patches = [
#     "galaxynext.patches.add_number_of_prints_cf"
# ]

# it's for custom hooks, you can add your own hooks here ---

# doc_events = {
#     "Item": {
#         "validate": "galaxynext.item_hooks.update_item_fields",
#         "on_update": "galaxynext.item_hooks.rename_item_after_save"
#     }
# }
 
# hooks.py

doc_events = {
    "Item": {
        # Before save → update fields
        "before_save": "galaxynext.item_hooks.update_item_fields",

        # After save → rename if needed
        "after_insert": "galaxynext.item_hooks.rename_item_after_save",
        "on_update": "galaxynext.item_hooks.rename_item_after_save",
    }
}

# -------------------------------------
  
fixtures = [
    {
        "dt": "Client Script",
        "filters": [["name", "in", [
            "Item Group - Default Parameter Row",
            "12_08_item-parameter",
            "ItemCode_to_Description",
            "Hide_Add_Row_Tab",
	    "Trantype-E_D"
        ]]]
    },
    {
        "dt": "Server Script",
        "filters": [["name", "in", [
            "itemcode_edit_tab"
        ]]]
    }
]


# Include custom JS and CSS in Desk
app_include_css = "/assets/galaxynext/css/galaxyerp.css"
app_include_js = [
    "/assets/galaxynext/js/galaxyerp.js",
    "/assets/galaxynext/js/custom_about.js"
]

# Include custom JS and CSS in Web Templates
web_include_css = "/assets/galaxynext/css/galaxyerp.css"
web_include_js = [
    "/assets/galaxynext/js/galaxyerp.js",
    "/assets/galaxynext/js/custom_about.js"
]

# Website context for logo overrides
website_context = {
    "favicon": "/assets/galaxynext/images/galaxynext_logo.png",
    "splash_image": "/assets/galaxynext/images/galaxynext_logo.png",
    "app_logo_url": "/assets/galaxynext/images/galaxynext_logo.png",
    "brand_logo": "/assets/galaxynext/images/galaxynext_logo.png",
    "footer_logo": "/assets/galaxynext/images/galaxynext_logo.png",
    "login_with_email_link": True
}

# Override favicon for all contexts
favicon = "/assets/galaxynext/images/galaxynext_logo.png"

# Override the About dialog JS from Frappe
override_include_files = {
    "frappe/public/js/frappe/ui/toolbar/about.js": "/assets/galaxynext/js/custom_about.js",
    "frappe/public/js/frappe/help/onboarding.js": "/assets/galaxynext/js/custom_onboarding.js",
    "erpnext/erpnext/setup/onboarding_step/create_an_item/create_an_item.json": "/assets/galaxynext/js/create_an_item.json"
}

onboarding_steps = {
    "Item": "galaxynext.setup.onboarding_step.create_an_item.create_an_item"
}


# App logo for top left corner
app_logo_url = "/assets/galaxynext/images/galaxynext_logo.png"

# ✅ Add this line for translation override:
translated_languages = ["en"]

# If needed in the future, you can override whitelisted methods here:
# override_whitelisted_methods = {
#     "frappe.widgets.onboarding_widget.get_onboarding_data": "galaxynext.utils.onboarding_widget_override.get_onboarding_widget_data_override",
#     "frappe.widgets.onboarding_widget.get_step_data": "galaxynext.utils.onboarding_widget_override.override_onboarding_step_data"
# }