frappe.provide("frappe.ui.misc");

frappe.ui.misc.about = function () {
	if (!frappe.ui.misc.about_dialog) {
		const d = new frappe.ui.Dialog({ title: __("GalaxyNext Framework") });

		$(d.body).html(`
			<div>
				<p><b>GalaxyNext – Powered ERP Framework</b></p>
				<p><i class='fa fa-globe fa-fw'></i>
					Website:
					<a href='https://galaxyerpsoftware.com' target='_blank'>https://galaxyerpsoftware.com</a></p>
				<p><i class='fa fa-github fa-fw'></i>
					Source:
					<a href='https://github.com/GalaxyERPSoftware/GalaxyNext' target='_blank'>GitHub Repo</a></p>
				<p><i class='fa fa-book fa-fw'></i>
					Documentation:
					<a href='https://docs.galaxyerpsoftware.com' target='_blank'>docs.galaxyerpsoftware.com</a></p>
				<p><i class='fa fa-linkedin fa-fw'></i>
					LinkedIn:
					<a href='https://www.linkedin.com/company/galaxy-erp-software-private-limited' target='_blank'>Galaxy ERP</a></p>
				<p><i class='fa fa-instagram fa-fw'></i>
					Instagram:
					<a href='https://www.instagram.com/galaxyerpsoftwarepvtltd' target='_blank'>@galaxyerpsoftwarepvtltd</a></p>
				<hr>
				<h4>Installed Apps</h4>
				<div id='about-app-versions'>Loading versions...</div>
				<hr>
				<p class='text-muted'>© GalaxyERP Software Pvt. Ltd. and contributors</p>
			</div>`);

		frappe.ui.misc.about_dialog = d;

		frappe.ui.misc.about_dialog.on_page_show = function () {
			if (!frappe.versions) {
				frappe.call({
					method: "frappe.utils.change_log.get_versions",
					callback: function (r) {
						show_versions(r.message);
					},
				});
			} else {
				show_versions(frappe.versions);
			}
		};

		function show_versions(versions) {
			const $wrap = $("#about-app-versions").empty();
			Object.keys(versions).sort().forEach(function (key) {
				const v = versions[key];
				let text = v.branch
					? `<p><b>${v.title}:</b> v${v.branch_version || v.version} (${v.branch})<br></p>`
					: `<p><b>${v.title}:</b> v${v.version}<br></p>`;
				$(text).appendTo($wrap);
			});
			frappe.versions = versions;
		}
	}

	frappe.ui.misc.about_dialog.show();
};