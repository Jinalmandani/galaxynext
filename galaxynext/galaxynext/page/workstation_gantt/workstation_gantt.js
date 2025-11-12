// frappe.pages['workstation-gantt'].on_page_load = function (wrapper) {
//   const page = frappe.ui.make_app_page({
//     parent: wrapper,
//     title: 'Workstation Gantt View',
//     single_column: true,
//   });

//   $(frappe.render_template("workstation_gantt", {})).appendTo(page.body);

//   frappe.require([
//     "https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js",
//   ], () => {
//     load_workorders();
//   });
// };

// // -----------------------------
// // Fetch Work Orders (Server-side Whitelisted Method)
// // -----------------------------
// function load_workorders() {
//   frappe.call({
//     method: "galaxynext.galaxynext.page.workstation_gantt.workstation_gantt.get_workorders",
//     callback: function (r) {
//       if (!r.message || r.message.length === 0) {
//         frappe.show_alert({ message: "No Work Orders found.", indicator: "orange" });
//         return;
//       }

//       const events = r.message.map((wo) => ({
//         id: wo.name,
//         title: `${wo.name} - ${wo.production_item}`,
//         start: wo.planned_start_date,
//         end: wo.planned_end_date,
//         workstation: wo.workstation,
//       }));

//       render_calendar(events);
//     },
//   });
// }

// // -----------------------------
// // Render FullCalendar Gantt View
// // -----------------------------
// function render_calendar(events) {
//   const calendarEl = document.getElementById("calendar");
//   if (!calendarEl) {
//     frappe.show_alert({ message: "❌ Calendar element not found!", indicator: "red" });
//     return;
//   }

//   const calendar = new FullCalendar.Calendar(calendarEl, {
//     initialView: "dayGridMonth",
//     editable: true,
//     eventStartEditable: true,
//     eventDurationEditable: true,
//     events: events,

//     eventDidMount: function (info) {
//       const ws = info.event.extendedProps.workstation || "";
//       if (ws) {
//         const wsDiv = document.createElement("div");
//         wsDiv.style.fontSize = "11px";
//         wsDiv.style.color = "#94a3b8";
//         wsDiv.innerText = ws;
//         info.el.appendChild(wsDiv);
//       }
//     },

//     // Drag event (change start/end)
//     eventDrop: function (info) {
//       update_workorder(info.event.id, {
//         planned_start_date: info.event.startStr,
//         planned_end_date: info.event.endStr || info.event.startStr,
//       }, info);
//     },

//     // Resize event (change end date)
//     eventResize: function (info) {
//       update_workorder(info.event.id, {
//         planned_end_date: info.event.endStr,
//       }, info);
//     },

//     // Click to change workstation
//     eventClick: function (info) {
//       const currentWS = info.event.extendedProps.workstation || "";
//       const newWS = prompt(`Current Workstation: ${currentWS}\nEnter new workstation:`);
//       if (newWS && newWS.trim() !== "") {
//         update_workorder(info.event.id, { workstation: newWS }, info);
//         info.event.setExtendedProp("workstation", newWS);
//       }
//     },
//   });

//   calendar.render();
// }

// // -----------------------------
// // Update Work Order via Server
// // -----------------------------
// function update_workorder(workOrderId, data, info) {
//   frappe.call({
//     method: "galaxynext.galaxynext.page.workstation_gantt.workstation_gantt.update_workorder",
//     args: {
//       work_order_id: workOrderId,
//       data: data,
//     },
//     callback: function (r) {
//       if (r.exc) {
//         frappe.show_alert({ message: "❌ Failed to update Work Order", indicator: "red" });
//         info.revert();
//       } else {
//         frappe.show_alert({ message: "✅ Work Order updated", indicator: "green" });
//       }
//     },
//     error: function () {
//       frappe.show_alert({ message: "⚠️ Server communication error", indicator: "orange" });
//       info.revert();
//     },
//   });
// }



// ----working console ma aave che

// frappe.pages['workstation-gantt'].on_page_load = function(wrapper) {
//   new WorkstationGantt(wrapper);
// };

// class WorkstationGantt {
//   constructor(wrapper) {
//     this.wrapper = wrapper; // ✅ keep original wrapper element
//     this.make();
//   }

//   async make() {
//     // Proper way to create page in Frappe v15
//     this.page = frappe.ui.make_app_page({
//       parent: this.wrapper,
//       title: 'Workstation Gantt View',
//       single_column: true
//     });

//     // ✅ Correct DOM append for Frappe v15
//     const ganttDiv = document.createElement("div");
//     ganttDiv.id = "workstation-gantt";
//     ganttDiv.style.height = "80vh";
//     ganttDiv.style.width = "100%";
//     ganttDiv.style.marginTop = "20px";
//     this.page.main.append(ganttDiv);  // ← FIXED

//     // Now render calendar
//     this.render_gantt();
//   }

//   async render_gantt() {
//     console.log("🔹 Fetching data for Workstation Gantt...");
//     try {
//       let result = await frappe.call({
//         method: "galaxynext.galaxynext.page.workstation_gantt.workstation_gantt.get_workorders"
//       });

//       console.log("✅ Server result:", result);
//       let data = result.message || [];

//       if (!data.length) {
//         frappe.msgprint("No Work Orders found!");
//         return;
//       }

//       let workstations = [...new Set(data.map(d => d.workstation || "Unassigned"))];
//       let resources = workstations.map(w => ({ id: w, title: w }));
//       let events = data.map(d => ({
//         id: d.name,
//         resourceId: d.workstation || "Unassigned",
//         title: `${d.name} - ${d.production_item}`,
//         start: d.planned_start_date,
//         end: d.planned_end_date,
//         backgroundColor: "#7289da"
//       }));

//       const calendarEl = document.getElementById("workstation-gantt");
//       console.log("🔹 Initializing FullCalendar...");

//       const calendar = new FullCalendar.Calendar(calendarEl, {
//         schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
//         initialView: "resourceTimelineWeek",
//         resourceAreaHeaderContent: "Workstations",
//         resources,
//         events,
//         editable: true,
//         aspectRatio: 1.8,
//         eventDrop: async (info) => await this.update_workorder(info.event),
//         eventResize: async (info) => await this.update_workorder(info.event),
//         headerToolbar: {
//           left: "today prev,next",
//           center: "title",
//           right: "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth"
//         }
//       });

//       calendar.render();
//       console.log("✅ Gantt loaded successfully!");
//     } catch (e) {
//       console.error("❌ Error in render_gantt:", e);
//       frappe.msgprint("Error loading Gantt View. Check console for details.");
//     }
//   }

//   async update_workorder(event) {
//     console.log("🔹 Updating:", event.id);
//     await frappe.call({
//       method: "galaxynext.galaxynext.page.workstation_gantt.workstation_gantt.update_workorder",
//       args: {
//         work_order_id: event.id,
//         data: {
//           planned_start_date: event.startStr,
//           planned_end_date: event.endStr,
//           workstation: event.getResources()[0]?.id
//         }
//       }
//     });
//     frappe.show_alert({ message: __("Work Order Updated"), indicator: "green" });
//   }
// }






frappe.pages['workstation-gantt'].on_page_load = function(wrapper) {
  new WorkstationGantt(wrapper);
};

class WorkstationGantt {
  constructor(wrapper) {
    this.wrapper = wrapper;
    this.page = null;
    this.calendar = null;
    this.make();
  }

  async make() {
    this.page = frappe.ui.make_app_page({
      parent: this.wrapper,
      title: 'Workstation Gantt View',
      single_column: true
    });

    this.page.add_button('Refresh', () => this.render_gantt(), { icon: 'refresh' });

    this.page.add_field({
      fieldname: 'workstation_filter',
      label: __('Workstation'),
      fieldtype: 'Link',
      options: 'Workstation',
      change: () => this.render_gantt()
    });

    const ganttDiv = `
      <div id="workstation-gantt-container" style="padding: 20px;">
        <div id="workstation-gantt" style="height: 75vh; width: 100%; background: white; border: 1px solid #d1d8dd; border-radius: 4px;"></div>
      </div>
    `;
    $(this.page.body).html(ganttDiv);

    await this.load_fullcalendar();
    this.render_gantt();
  }

  async load_fullcalendar() {
    return new Promise((resolve, reject) => {
      if (window.FullCalendar) return resolve();

      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/fullcalendar-scheduler@6.1.10/index.global.min.js';
      script.onload = () => {
        console.log('✅ FullCalendar Scheduler loaded');
        resolve();
      };
      script.onerror = () => {
        frappe.msgprint('Failed to load FullCalendar Scheduler');
        reject();
      };
      document.head.appendChild(script);
    });
  }

  async render_gantt() {
    try {
      frappe.show_alert({ message: __("Loading Gantt View..."), indicator: "blue" });

      const workstation_filter = this.page.fields_dict.workstation_filter?.get_value();

      let result = await frappe.call({
        method: "galaxynext.galaxynext.page.workstation_gantt.workstation_gantt.get_workorders",
        args: { workstation: workstation_filter }
      });

      let data = result.message || [];
      if (!data.length) {
        frappe.msgprint(__("No Work Orders found!"));
        return;
      }

      console.log('📊 Work Orders:', data);

      // Unique Workstations
      let workstations = [...new Set(data.map(d => d.workstation || "Unassigned"))];
      let colors = ['#7289da', '#43b581', '#faa61a', '#f04747', '#9c59b6', '#3498db', '#e91e63', '#00bcd4'];

      let resources = workstations.map((w, i) => ({
        id: w,
        title: w,
        eventBackgroundColor: colors[i % colors.length]
      }));

      let events = data.map(d => ({
        id: d.name,
        resourceId: d.workstation || "Unassigned",
        title: d.name,
        start: d.planned_start_date,
        end: d.planned_end_date,
        extendedProps: {
          production_item: d.production_item,
          status: d.status
        }
      }));

      if (this.calendar) this.calendar.destroy();

      const calendarEl = document.getElementById("workstation-gantt");
      this.calendar = new FullCalendar.Calendar(calendarEl, {
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        initialView: 'resourceTimelineWeek',
        resourceAreaHeaderContent: 'Workstations',
        resources: resources,
        events: events,
        editable: true,
        droppable: true,
        selectable: true,
        height: 'auto',

        headerToolbar: {
          left: 'today prev,next',
          center: 'title',
          right: 'resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth'
        },

        resourceAreaWidth: '18%',

        eventContent: function(arg) {
          return {
            html: `
              <div style="padding: 4px 8px; font-size: 12px;">
                <div style="font-weight: 600;">${arg.event.id}</div>
                <div style="font-size: 11px; opacity: 0.8;">${arg.event.extendedProps.production_item}</div>
              </div>
            `
          };
        },

        eventDrop: async (info) => await this.handle_event_update(info, 'moved'),
        eventResize: async (info) => await this.handle_event_update(info, 'resized'),
        eventClick: (info) => frappe.set_route('Form', 'Work Order', info.event.id),

        eventDidMount: function(info) {
          $(info.el).tooltip({
            title: `${info.event.id}\n${info.event.extendedProps.production_item}\n${info.event.startStr} → ${info.event.endStr}`,
            placement: 'top',
            trigger: 'hover',
            container: 'body'
          });
        }
      });

      this.calendar.render();
      frappe.show_alert({ message: __("✅ Gantt View Loaded Successfully"), indicator: "green" });

    } catch (e) {
      console.error("❌ Gantt Load Error:", e);
      frappe.msgprint("Error loading Gantt View: " + e.message);
    }
  }

  async handle_event_update(info, action) {
    try {
      const event = info.event;
      const pad = (n) => n.toString().padStart(2, '0');
      const formatDate = (dt) => `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}:${pad(dt.getSeconds())}`;

      const data = {
        planned_start_date: formatDate(event.start),
        planned_end_date: event.end ? formatDate(event.end) : formatDate(event.start)
      };

      const res = event.getResources();
      if (res.length > 0) data.workstation = res[0].id;

      console.log("📤 Updating Work Order:", event.id, data);

      const result = await frappe.call({
        method: "galaxynext.galaxynext.page.workstation_gantt.workstation_gantt.update_workorder",
        args: {
          work_order_id: event.id,
          data: data
        }
      });

      if (result.message.status === 'success') {
        frappe.show_alert({ message: __(`Work Order ${action} successfully!`), indicator: "green" });
      } else {
        throw new Error(result.message.message);
      }

    } catch (e) {
      console.error("❌ Update failed:", e);
      info.revert();
      frappe.show_alert({ message: __("Failed to update: ") + e.message, indicator: "red" });
    }
  }
}
