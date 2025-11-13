// Function to replace logos with GalaxyNext logo
function replaceLogos() {
    $('.navbar-brand .app-logo, .app-logo').each(function() {
        if ($(this).attr('src') && !$(this).attr('src').includes('galaxynext_logo')) {
            $(this).attr('src', '/assets/galaxynext/images/galaxynext_logo.png');
        }
    });
    $('link[rel="shortcut icon"], link[rel="icon"]').each(function() {
        if ($(this).attr('href') && !$(this).attr('href').includes('galaxynext_logo')) {
            $(this).attr('href', '/assets/galaxynext/images/galaxynext_logo.png');
        }
    });
    $('.splash img').each(function() {
        if ($(this).attr('src') && !$(this).attr('src').includes('galaxynext_logo')) {
            $(this).attr('src', '/assets/galaxynext/images/galaxynext_logo.png');
        }
    });
    $('.footer-logo img').each(function() {
        if ($(this).attr('src') && !$(this).attr('src').includes('galaxynext_logo')) {
            $(this).attr('src', '/assets/galaxynext/images/galaxynext_logo.png');
        }
    });
    $('img[src*="frappe-framework-logo"], img[src*="erpnext-logo"], img[src*="frappe-favicon"]').each(function() {
        $(this).attr('src', '/assets/galaxynext/images/galaxynext_logo.png');
    });
}


function applyGalaxyNextBranding() {
    replaceLogos();
    replaceBranding();
}

// Set app logo URL
if (typeof frappe !== 'undefined' && frappe.boot) {
    frappe.boot.app_logo_url = '/assets/galaxynext/images/galaxynext_logo.png';
}

