app_name = "galaxynext"
app_title = "galaxynext"
app_publisher = "khushi"
app_description = "text change"
app_email = "khushim@gmail.com"
app_license = "mit"



override_whitelisted_methods = {
    "galaxynext.api.get_miscellaneous_options": "galaxynext.api.get_miscellaneous_options"
}


# Hook into document events for Item
doc_events = {
    "Item": {
        # Before save → update fields
        "before_save": "galaxynext.item_hooks.update_item_fields",

        # After save → rename if needed
        "after_insert": "galaxynext.item_hooks.rename_item_after_save",
        "on_update": "galaxynext.item_hooks.rename_item_after_save",
    }
}






# ===== Desk Customizations =====
app_include_css = "/assets/galaxynext/css/galaxyerp.css"
app_include_js = [
    "/assets/galaxynext/js/galaxyerp.js",
    "/assets/galaxynext/js/custom_about.js",
    "/assets/galaxynext/js/toolbar/help_dropdown.js"  # ✅ Custom Help Dropdown JS
]

# ===== Web Templates Customizations =====
web_include_css = "/assets/galaxynext/css/galaxyerp.css"
web_include_js = [
    "/assets/galaxynext/js/galaxyerp.js",
    "/assets/galaxynext/js/custom_about.js"
]

# ===== Website Context Overrides =====
website_context = {
    "favicon": "/assets/galaxynext/images/galaxynext_logo.png",
    "splash_image": "/assets/galaxynext/images/galaxynext_logo.png",
    "app_logo_url": "/assets/galaxynext/images/galaxynext_logo.png",
    "brand_logo": "/assets/galaxynext/images/galaxynext_logo.png",
    "footer_logo": "/assets/galaxynext/images/galaxynext_logo.png",
    "login_with_email_link": True
}

# ===== Global Favicon =====
favicon = "/assets/galaxynext/images/galaxynext_logo.png"

# ===== JS Override Files (Override Core Files) =====
override_include_files = {
    "frappe/public/js/frappe/ui/toolbar/about.js": "/assets/galaxynext/js/custom_about.js",
    "frappe/public/js/frappe/help/onboarding.js": "/assets/galaxynext/js/custom_onboarding.js",
    "erpnext/erpnext/setup/onboarding_step/create_an_item/create_an_item.json": "/assets/galaxynext/js/create_an_item.json"
}

# ===== Onboarding Step Override =====
onboarding_steps = {
    "Item": "galaxynext.setup.onboarding_step.create_an_item.create_an_item"
}

# ===== App Logo (Top Left) =====
app_logo_url = "/assets/galaxynext/images/galaxynext_logo.png"

# ===== App Logo (For App Selector Screen) =====
app_logo = "/assets/galaxynext/images/Galaxynext.png"


# ===== Language Support =====
translated_languages = ["en"]

# ===== ✅ Help Dropdown Whitelisted Override (IMPORTANT) =====
override_whitelisted_methods = {
    "frappe.desk.utils.get_help_links": "galaxynext.utils.custom_toolbar.get_help_links"
}

fixtures = [
    {
        "dt": "Client Script",
        "filters": [["name", "in", [
            "project script",
            "customer testing script",
            "supplier testing script",
            "jab card testing client script",
	        "work order client script",
            "campaign client script",
            "opportunity client script",
            "lead client script",
            "contract client script",
            "prospect client script",
	        "GERP client script",
            "fetch item parameter",
            "Get Original Tab Table detail"
           

        ]]]
    },
    {
        "dt": "Server Script",
        "filters": [["name", "in", [
            "job card test server script",
            "company event"
        ]]]
    }
]
