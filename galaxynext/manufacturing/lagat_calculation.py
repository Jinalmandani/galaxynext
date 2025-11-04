# import frappe

# @frappe.whitelist()
# def calculate_lagat(rawmaterial, design_per, cut_loop, cat_ae, pileheight, ply, area, wastage, twist):
#     try:
#         result = frappe.db.sql("""
#             SELECT GetLagatz(%s, %s, %s, %s, %s, %s, %s, %s, %s) AS sqyard_value
#         """, (rawmaterial, design_per, cut_loop, cat_ae, pileheight, ply, area, wastage, twist), as_dict=True)

#         return result[0].sqyard_value if result else 0
#     except Exception as e:
#         frappe.log_error(message=str(e), title="Lagat Function Error")
#         return 0







# import frappe

# @frappe.whitelist(allow_guest=True)
# def calculate_lagat_auto(parent_design=None):
#     if not parent_design:
#         return {"error": "Parent design not provided"}

#     # --- Fetch Area & PileHeight from MiscellaneousMst ---
#     area = frappe.db.get_value("MiscellaneousMst", {"Trantype": "AREA"}, "remark") or 0
#     pileheight = frappe.db.get_value("MiscellaneousMst", {"Trantype": "PILEHEIGHT"}, "remark") or 0

#     # --- Prepare results ---
#     results = []
#     updated = 0

#     # --- Fetch design portion data ---
#     portions = frappe.db.sql("""
#         SELECT 
#             idx,
#             raw_material,
#             twistnontwist,
#             TRIM(SUBSTRING_INDEX(color_name, '+', 1)) AS color_part,
#             TRIM(SUBSTRING_INDEX(pile, '+', 1)) AS color_ply,
#             total_ply,
#             percentage * TRIM(SUBSTRING_INDEX(pile, '+', 1)) / total_ply AS design_per
#         FROM `tabProduction Design Portion`
#         WHERE parent = %s
#     """, (parent_design,), as_dict=True)

#     for row in portions:
#         # Get Raw Material rate from MiscellaneousMst
#         raw_rate = frappe.db.get_value(
#             "MiscellaneousMst",
#             {"Trantype": "RAW MATERIAL TYPE", "Value": row.raw_material},
#             "remark"
#         ) or 0

#         # Get Cut Loop value from MiscellaneousMst
#         cut_loop = frappe.db.get_value(
#             "MiscellaneousMst",
#             {"Trantype": "CUT_LOOP", "Value": "CUT 2x2"},
#             "remark"
#         ) or 0

#         # Twist logic (1 for Twist, 0 for Non-Twist)
#         twist = 1 if (row.twistnontwist or "").upper() == "TWIST" else 0

#         # Constant values
#         cat_ae = "Cat_E"
#         wastage = 0.007

#         # --- Run SQL Function GetLagatz() ---
#         result = frappe.db.sql("""
#             SELECT GetLagatz(%s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """, (
#             raw_rate,                # Raw Material Rate
#             row.design_per,          # Design Percentage
#             cut_loop,                # Cut Loop
#             cat_ae,                  # Category AE
#             pileheight,              # Pile Height
#             row.color_ply,           # Ply (from pile)
#             area,                    # Area
#             wastage,                 # Wastage
#             twist                    # Twist / Non-Twist
#         ))

#         lagat_value = result[0][0] if result and result[0][0] else 0

#         # --- Update Production Design Portion ---
#         frappe.db.set_value("Production Design Portion", row.idx, "qty", lagat_value)
#         updated += 1
#         results.append(f"{row.raw_material} → qty: {lagat_value}")

#     frappe.db.commit()

#     return {
#         "message": "Lagat calculation completed successfully",
#         "updated_rows": updated,
#         "sample_results": results
#     }





# popup ma show thay value

# import frappe

# @frappe.whitelist()
# def get_lagatz_auto():
#     try:
#         # ---------------------------------------------
#         # 1️⃣ Fetch Values from MiscellaneousMst (trantype)
#         # ---------------------------------------------
#         rawmaterial = frappe.db.get_value("MiscellaneousMst", {"trantype": "TM-10-2025-00062"}, "remark")
#         cut_loop = frappe.db.get_value("MiscellaneousMst", {"trantype": "TM-09-2025-00049"}, "remark")

#         # ---------------------------------------------
#         # 2️⃣ Fetch Design_Per, Ply, Twist from tabProduction Design Portion
#         # ---------------------------------------------
#         sql = """
#             SELECT 
#                 COALESCE(SUM(percentage), 0) AS percentage,
#                 COALESCE(SUM(total_ply), 0) AS total_ply,
#                 MAX(twistnontwist) AS twistnontwist
#             FROM (
#                 SELECT 
#                     TRIM(SUBSTRING_INDEX(color_name, '+', 1)) AS color_part,
#                     TRIM(SUBSTRING_INDEX(pile, '+', 1)) AS color_ply,
#                     raw_material,
#                     twistnontwist,
#                     total_ply,
#                     percentage
#                 FROM `tabProduction Design Portion`
#                 WHERE parent = 'DSG-IMP-2025-000006'
#                 UNION ALL
#                 SELECT 
#                     TRIM(SUBSTRING_INDEX(color_name, '+', -1)) AS color_part,
#                     TRIM(SUBSTRING_INDEX(pile, '+', -1)) AS color_ply,
#                     raw_material,
#                     twistnontwist,
#                     total_ply,
#                     percentage
#                 FROM `tabProduction Design Portion`
#                 WHERE color_name LIKE '%+%' AND parent = 'DSG-IMP-2025-000006'
#             ) AS combined;
#         """

#         result = frappe.db.sql(sql, as_dict=True)
#         design_per = float(result[0].percentage or 0)
#         ply = float(result[0].total_ply or 0)
#         twist = result[0].twistnontwist or ""

#         # ---------------------------------------------
#         # 3️⃣ Fixed / Static Values
#         # ---------------------------------------------
#         cat_ae = "Cat_C"
#         pile_height = 10
#         area = 194.62
#         wastage = 0.007

#         # ---------------------------------------------
#         # 4️⃣ Validate Required Fields
#         # ---------------------------------------------
#         if not rawmaterial or not cut_loop:
#             frappe.msgprint(f"❌ Missing data — RawMaterial: {rawmaterial}, Cut_Loop: {cut_loop}")
#             return 0

#         # ---------------------------------------------
#         # 5️⃣ Call SQL Function GetLagatz (9 parameters)
#         # ---------------------------------------------
#         query = """
#             SELECT GetLagatz1(%s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         lagatz_value = frappe.db.sql(
#             query,
#             (
#                 rawmaterial,
#                 design_per,
#                 cut_loop,
#                 cat_ae,
#                 pile_height,
#                 ply,
#                 area,
#                 wastage,
#                 twist
#             ),
#         )[0][0]

#         # ---------------------------------------------
#         # 6️⃣ Display Results in Frappe
#         # ---------------------------------------------
#         frappe.msgprint(f"""
#             🧩 <b>Fetched Values</b><br>
#             Raw Material: {rawmaterial}<br>
#             Design_Per: {design_per}<br>
#             Cut_Loop: {cut_loop}<br>
#             Cat_AE: {cat_ae}<br>
#             Pile Height: {pile_height}<br>
#             Ply: {ply}<br>
#             Area: {area}<br>
#             Wastage: {wastage}<br>
#             Twist: {twist}<br>
#             ✅ <b>Lagat Calculated:</b> {lagatz_value}
#         """)

#         return lagatz_value

#     except Exception as e:
#         frappe.log_error(message=str(e), title="GetLagatz Error")
#         frappe.msgprint(f"❌ Error: {str(e)}")
#         return 0



# import frappe

# @frappe.whitelist()
# def get_lagatz_auto():
#     try:
#         # ---------------------------------------------
#         # 1️⃣ Fetch Values from MiscellaneousMst (trantype)
#         # ---------------------------------------------
#         rawmaterial = frappe.db.get_value("MiscellaneousMst", {"trantype": "TM-10-2025-00062"}, "remark")
#         cut_loop = frappe.db.get_value("MiscellaneousMst", {"trantype": "TM-09-2025-00049"}, "remark")

#         # ---------------------------------------------
#         # 2️⃣ Temporarily use fixed Design_Per & Ply
#         # ---------------------------------------------
#         design_per = 13.20
#         ply = 3

#         # ---------------------------------------------
#         # 3️⃣ Fetch Twist from tabProduction Design Portion
#         # ---------------------------------------------
#         twist = frappe.db.get_value(
#             "Production Design Portion",
#             {"parent": "DSG-IMP-2025-000006"},
#             "twistnontwist"
#         ) or ""

#         # ---------------------------------------------
#         # 4️⃣ Fixed / Static Values
#         # ---------------------------------------------
#         cat_ae = "Cat_C"
#         pile_height = 10
#         area = 194.62
#         wastage = 0.007

#         # ---------------------------------------------
#         # 5️⃣ Validate Required Fields
#         # ---------------------------------------------
#         if not rawmaterial or not cut_loop:
#             frappe.msgprint(f"❌ Missing data — RawMaterial: {rawmaterial}, Cut_Loop: {cut_loop}")
#             return 0

#         # ---------------------------------------------
#         # 6️⃣ Call SQL Function GetLagatz1 (9 parameters)
#         # ---------------------------------------------
#         query = """
#             SELECT GetLagatz1(%s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         lagatz_value = frappe.db.sql(
#             query,
#             (
#                 rawmaterial,
#                 design_per,
#                 cut_loop,
#                 cat_ae,
#                 pile_height,
#                 ply,
#                 area,
#                 wastage,
#                 twist
#             ),
#         )[0][0]

#         # ---------------------------------------------
#         # 7️⃣ Display Results
#         # ---------------------------------------------
#         frappe.msgprint(f"""
#             🧩 <b>Fetched Values</b><br>
#             Raw Material: {rawmaterial}<br>
#             Design_Per: {design_per}<br>
#             Cut_Loop: {cut_loop}<br>
#             Cat_AE: {cat_ae}<br>
#             Pile Height: {pile_height}<br>
#             Ply: {ply}<br>
#             Area: {area}<br>
#             Wastage: {wastage}<br>
#             Twist: {twist}<br>
#             ✅ <b>Lagat Calculated:</b> {lagatz_value}
#         """)

#         return lagatz_value

#     except Exception as e:
#         frappe.log_error(message=str(e), title="GetLagatz Error")
#         frappe.msgprint(f"❌ Error: {str(e)}")
#         return 0








# import frappe

# @frappe.whitelist()
# def calculate_lagat_details(design_id):
#     """
#     Fetch all parameters for given design_id,
#     call SQL function GetLagatz() row-wise,
#     return per-row breakdown and total.
#     """

#     rows = frappe.db.sql("""
#         SELECT idx,
#             TRIM(SUBSTRING_INDEX(color_name, '+', 1)) AS color_part,
#             TRIM(SUBSTRING_INDEX(pile, '+', 1)) AS color_ply,
#             raw_material,
#             total_ply,
#             percentage * TRIM(SUBSTRING_INDEX(pile, '+', 1)) / total_ply AS Colour_per,
#             match_item,
#             twistnontwist
#         FROM `tabProduction Design Portion`
#         WHERE parent=%(design_id)s
#         UNION ALL
#         SELECT idx,
#             TRIM(SUBSTRING_INDEX(color_name, '+', -1)) AS color_part,
#             TRIM(SUBSTRING_INDEX(pile, '+', -1)) AS color_ply,
#             raw_material,
#             total_ply,
#             percentage * TRIM(SUBSTRING_INDEX(pile, '+', -1)) / total_ply AS Colour_per,
#             match_item,
#             twistnontwist
#         FROM `tabProduction Design Portion`
#         WHERE color_name LIKE '%+%'
#         AND parent=%(design_id)s
#     """, {"design_id": design_id}, as_dict=True)

#     if not rows:
#         frappe.throw("No Production Design Portion data found for this design.")

#     total_lagat = 0
#     result_rows = []

#     # constants
#     wastage = 0.007
#     cat_ae = "Cat_A"  # fixed for now (you can make it user-input later)
#     area = frappe.db.get_value(
#         "MiscellaneousMst",
#         {"trantype": ("in", frappe.db.get_all("TrantypeMst",
#                 filters={"trantypename": "AREA"}, pluck="name"))},
#         "remark"
#     ) or 1.0

#     for r in rows:
#         rawmaterial = frappe.db.get_value(
#             "MiscellaneousMst",
#             {"trantype": ("in", frappe.db.get_all("TrantypeMst",
#                     filters={"trantypename": "RAW MATERIAL TYPE"}, pluck="name")),
#              "value": r.raw_material},
#             "remark"
#         ) or 0

#         design_per = float(r.Colour_per or 0)
#         cut_loop = frappe.db.get_value(
#             "MiscellaneousMst",
#             {"trantype": ("in", frappe.db.get_all("TrantypeMst",
#                     filters={"trantypename": "CUT_LOOP"}, pluck="name")),
#              "value": r.match_item},
#             "remark"
#         ) or 0

#         pileheight = frappe.db.get_value(
#             "MiscellaneousMst",
#             {"trantype": ("in", frappe.db.get_all("TrantypeMst",
#                     filters={"trantypename": "PILEHEIGHT"}, pluck="name")),
#              "value": r.color_ply},
#             "remark"
#         ) or float(r.color_ply or 0)

#         ply = float(r.total_ply or 0)
#         twist = 1 if (r.twistnontwist or '').upper() == 'TWIST' else 0

#         # --- SQL Function Call ---
#         val = frappe.db.sql("""
#             SELECT GetLagatz(%s,%s,%s,%s,%s,%s,%s,%s,%s)
#         """, (
#             float(rawmaterial or 0),
#             design_per,
#             str(r.match_item or ''),
#             cat_ae,
#             float(pileheight or 0),
#             ply,
#             float(area or 1),
#             float(wastage),
#             twist
#         ))

#         lagat_value = float(val[0][0]) if val and val[0][0] else 0
#         total_lagat += lagat_value

#         result_rows.append({
#             "idx": r.idx,
#             "Color": r.color_part,
#             "RawMaterial": rawmaterial,
#             "PileHeight": pileheight,
#             "Ply": ply,
#             "Area": area,
#             "Design_Per": design_per,
#             "Twist": twist,
#             "Lagat": lagat_value
#         })

#     return {
#         "total": round(total_lagat, 4),
#         "rows": result_rows
#     }


#first code

# import frappe

# @frappe.whitelist()
# def calculate_lagat(design_no, cat_ae):
#     """
#     Calculate Lagat value for each color in the given Design.
#     Data fetched from tabProduction Design Portion and tabMiscellaneousMst.
#     """
#     try:
#         # --- Step 1: Fetch constants from MiscellaneousMst ---
#         area = get_misc_value("AREA")
#         pileheight = get_misc_value("PILEHEIGHT")
#         cut_loop = get_misc_value("CUT_LOOP")
#         wastage = 0.007  # fixed
#         cut_loop_remark = get_misc_remark("CUT_LOOP")

#         # --- Step 2: Fetch color-wise data from Production Design Portion ---
#         production_data = frappe.db.sql("""
#             SELECT color, rawmaterial, twist, percentage AS design_per, ply
#             FROM `tabProduction Design Portion`
#             WHERE parent = %s
#         """, (design_no,), as_dict=True)

#         if not production_data:
#             frappe.throw("No Production Design Portion data found for Design: {}".format(design_no))

#         results = []

#         # --- Step 3: Loop through each color and calculate Lagat ---
#         for row in production_data:
#             # Fetch rawmaterial remark from MiscellaneousMst
#             rawmaterial_remark = frappe.db.get_value(
#                 "MiscellaneousMst",
#                 {"trantype": "RAW MATERIAL TYPE", "value": row.rawmaterial},
#                 "remark"
#             ) or 0

#             # --- Step 4: Call SQL function GetLagatz ---
#             try:
#                 lagat = frappe.db.sql("""
#                     SELECT GetLagatz(%s,%s,%s,%s,%s,%s,%s,%s,%s)
#                 """, (
#                     rawmaterial_remark,
#                     row.design_per,
#                     cut_loop_remark,
#                     cat_ae,
#                     pileheight,
#                     row.ply,
#                     area,
#                     wastage,
#                     row.twist
#                 ))[0][0]

#             except Exception as e:
#                 frappe.log_error(f"Call to GetLagatz failed for color {row.color}: {str(e)}", "Lagat Calculation Error")
#                 lagat = 0

#             results.append({
#                 "color": row.color,
#                 "lagat": lagat
#             })

#         return results

#     except Exception as e:
#         frappe.log_error(f"Lagat Calculation Error: {str(e)}", "calculate_lagat")
#         frappe.throw(str(e))


# def get_misc_value(trantype):
#     """Fetch numeric value from MiscellaneousMst"""
#     return frappe.db.get_value("MiscellaneousMst", {"trantype": trantype}, "value") or 0


# def get_misc_remark(trantype):
#     """Fetch remark value from MiscellaneousMst"""
#     return frappe.db.get_value("MiscellaneousMst", {"trantype": trantype}, "remark") or ""


# import frappe
# from frappe import _

# @frappe.whitelist()
# def get_design_parameters(design_import_name):
#     """
#     Query Production Design Portion color-wise (returns list of dicts).
#     """
#     try:
#         # safe fetch to ensure doc exists
#         design_import = frappe.get_doc("Design Import", design_import_name)

#         color_data = frappe.db.sql("""
#             SELECT 
#                 idx,
#                 TRIM(SUBSTRING_INDEX(color_name, '+', 1)) AS color_part,
#                 TRIM(SUBSTRING_INDEX(pile, '+', 1)) AS color_ply,
#                 raw_material,
#                 total_ply,
#                 match_item,
#                 twist_non_twist,
#                 percentage * TRIM(SUBSTRING_INDEX(pile, '+', 1)) / total_ply AS colour_per
#             FROM `tabProduction Design Portion`
#             WHERE parent = %s

#             UNION ALL

#             SELECT 
#                 idx,
#                 TRIM(SUBSTRING_INDEX(color_name, '+', -1)) AS color_part,
#                 TRIM(SUBSTRING_INDEX(pile, '+', -1)) AS color_ply,
#                 raw_material,
#                 total_ply,
#                 match_item,
#                 twist_non_twist,
#                 percentage * TRIM(SUBSTRING_INDEX(pile, '+', -1)) / total_ply AS colour_per
#             FROM `tabProduction Design Portion`
#             WHERE color_name LIKE %s
#             AND parent = %s
#         """, (design_import_name, '%+%', design_import_name), as_dict=1)

#         return {"success": True, "color_data": color_data, "design_name": design_import.design_selection}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Design Parameters Error")
#         return {"success": False, "message": str(e)}


# @frappe.whitelist()
# def get_cut_loop_value(match_item):
#     """
#     Get numeric cut loop from MiscellaneousMst where trantype->trantypename = 'CUT_LOOP' and value = match_item.
#     """
#     try:
#         if not match_item:
#             return 0.0

#         res = frappe.db.sql("""
#             SELECT m.remark
#             FROM `tabMiscellaneousMst` m
#             LEFT JOIN `tabTrantypeMst` t ON m.trantype = t.name
#             WHERE t.trantypename = 'CUT_LOOP'
#             AND m.value = %s
#             LIMIT 1
#         """, (match_item,), as_dict=1)

#         if res and res[0].get("remark") not in (None, ""):
#             try:
#                 return float(res[0]["remark"])
#             except:
#                 return 0.0
#         return 0.0
#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Get Cut Loop Value Error")
#         return 0.0


# @frappe.whitelist()
# def get_raw_material_value(raw_material_name):
#     """
#     Return numeric remark value for raw material lookup.
#     """
#     try:
#         if not raw_material_name:
#             return 0.0

#         res = frappe.db.sql("""
#             SELECT remark
#             FROM `tabMiscellaneousMst`
#             WHERE value = %s
#             AND trantype = (
#                 SELECT name FROM `tabTrantypeMst` WHERE trantypename = 'RAW MATERIAL TYPE' LIMIT 1
#             )
#             LIMIT 1
#         """, (raw_material_name,), as_dict=1)

#         if res and res[0].get("remark") not in (None, ""):
#             try:
#                 return float(res[0]["remark"])
#             except:
#                 return 0.0
#         return 0.0
#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Get Raw Material Value Error")
#         return 0.0


# def calculate_cat_ae_value(category, pileheight, ply, cut_loop_value, twistnontwist):
#     """
#     Category calculation (wastage fixed 0.07). Twist/NonTwist handled per earlier logic.
#     """
#     wastage = 0.07
#     base_calc = (pileheight + 4) * ply * 0.036 * (0 + cut_loop_value + 0 + 0 + wastage)

#     category_percentages = {
#         'Cat_A': 0,
#         'Cat_B': 3.85,
#         'Cat_C': 7.70,
#         'Cat_D': 11.54,
#         'Cat_E': 15.38
#     }
#     percentage = category_percentages.get(category, 0)

#     # twistnontwist value in DB might be 'Twist' / 'NonTwist' or numeric 0
#     if twistnontwist in ('NonTwist', 'Non Twist', 0, '0', None):
#         if percentage == 0:
#             return base_calc
#         return (base_calc * percentage / 100.0) + base_calc
#     else:
#         # Twist
#         base_with_tw = base_calc + 0.31
#         if percentage == 0:
#             return base_with_tw
#         return (base_with_tw * percentage / 100.0) + base_with_tw


# @frappe.whitelist()
# def get_item_parameters(item_code):
#     """
#     Read AREA, PILEHEIGHT and Design Import from child table `tabItem Parameter`.
#     child table rows have fields: parameter, value (as per your screenshots).
#     Returns dict { area, pileheight, design_import }
#     """
#     try:
#         if not item_code:
#             return {'area': 0.0, 'pileheight': 0.0, 'design_import': None}

#         rows = frappe.db.sql("""
#             SELECT parameter, value
#             FROM `tabItem Parameter`
#             WHERE parent = %s
#         """, (item_code,), as_dict=1)

#         res = {'area': 0.0, 'pileheight': 0.0, 'design_import': None}

#         if not rows:
#             # no child rows found
#             return res

#         for r in rows:
#             param = (r.get('parameter') or '').strip().upper()
#             val = (r.get('value') or '').strip()
#             if param == 'AREA':
#                 try:
#                     res['area'] = float(val)
#                 except:
#                     res['area'] = 0.0
#             elif param == 'PILEHEIGHT' or param == 'PILE HEIGHT':
#                 try:
#                     res['pileheight'] = float(val)
#                 except:
#                     res['pileheight'] = 0.0
#             elif param in ('DESIGN IMPORT', 'DESIGN_IMPORT', 'DESIGN'):
#                 res['design_import'] = val

#         return res
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Item Parameters Error")
#         return {'area': 0.0, 'pileheight': 0.0, 'design_import': None}


# @frappe.whitelist()
# def calculate_lagat(item_code, category):
#     """
#     Main entry — called from client script.
#     Uses Item Parameter child table and Production Design Portion for color-wise calc.
#     """
#     try:
#         params = get_item_parameters(item_code)
#         area = params.get('area', 0.0)
#         pileheight = params.get('pileheight', 0.0)
#         design_import = params.get('design_import')

#         if not design_import:
#             return {"success": False, "message": "Design Import not found for this item"}

#         if area == 0 or pileheight == 0:
#             return {"success": False, "message": f"AREA or PILEHEIGHT not found. Area: {area}, PileHeight: {pileheight}"}

#         design_data = get_design_parameters(design_import)
#         if not design_data.get("success"):
#             return design_data

#         color_rows = design_data.get("color_data") or []
#         if not color_rows:
#             return {"success": False, "message": f"No color data found for Design Import: {design_import}"}

#         details = []
#         total_lagat = 0.0

#         for row in color_rows:
#             # safe numeric conversions
#             try:
#                 ply = float(row.get("color_ply") or 0)
#             except:
#                 ply = 0.0

#             try:
#                 design_per = float(row.get("colour_per") or 0)
#             except:
#                 design_per = 0.0

#             raw_material_multiplier = get_raw_material_value(row.get("raw_material"))
#             cut_loop_value = get_cut_loop_value(row.get("match_item"))

#             cat_ae_value = calculate_cat_ae_value(
#                 category,
#                 pileheight,
#                 ply,
#                 cut_loop_value,
#                 row.get("twist_non_twist")
#             )

#             # final lagat formula (following your provided formula)
#             # ((cat_ae_value * ply / ply) * area * design_per/100 * raw_material) / area  => simplifies to cat_ae_value * design_per/100 * raw_material
#             # But keeping original structure for clarity:
#             lagat = 0.0
#             if ply != 0:
#                 try:
#                     lagat = ((cat_ae_value * ply / ply) * area * design_per / 100.0 * raw_material_multiplier) / area
#                 except Exception:
#                     lagat = 0.0
#             else:
#                 # if ply zero, fallback to zero
#                 lagat = 0.0

#             details.append({
#                 "color_name": row.get("color_part"),
#                 "raw_material": row.get("raw_material"),
#                 "ply": ply,
#                 "design_per": design_per,
#                 "cut_loop_value": cut_loop_value,
#                 "raw_material_value": raw_material_multiplier,
#                 "cat_ae_value": cat_ae_value,
#                 "lagat": lagat
#             })
#             total_lagat += lagat

#         return {
#             "success": True,
#             "total_lagat": total_lagat,
#             "details": details,
#             "parameters": {
#                 "area": area,
#                 "pileheight": pileheight,
#                 "category": category,
#                 "design_import": design_import
#             }
#         }
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Calculate Lagat Error")
#         return {"success": False, "message": str(e)}



# # galaxynext/manufacturing/lagat_calculation.py
# import frappe
# from frappe import _
# from frappe.utils import flt

# @frappe.whitelist()
# def get_design_parameters(design_import_name):
#     """Return production design portion rows (handles +/- combined color names)."""
#     try:
#         if not design_import_name:
#             return {"success": False, "message": "Missing design_import_name"}

#         # ensure doc exists (will throw if not)
#         _ = frappe.get_doc("Design Import", design_import_name)

#         color_data = frappe.db.sql("""
#             SELECT 
#                 idx,
#                 TRIM(SUBSTRING_INDEX(color_name, '+', 1)) AS color_part,
#                 TRIM(SUBSTRING_INDEX(pile, '+', 1)) AS color_ply,
#                 raw_material,
#                 total_ply,
#                 match_item,
#                 twist_non_twist,
#                 percentage * TRIM(SUBSTRING_INDEX(pile, '+', 1)) / total_ply AS colour_per
#             FROM `tabProduction Design Portion`
#             WHERE parent = %s

#             UNION ALL

#             SELECT 
#                 idx,
#                 TRIM(SUBSTRING_INDEX(color_name, '+', -1)) AS color_part,
#                 TRIM(SUBSTRING_INDEX(pile, '+', -1)) AS color_ply,
#                 raw_material,
#                 total_ply,
#                 match_item,
#                 twist_non_twist,
#                 percentage * TRIM(SUBSTRING_INDEX(pile, '+', -1)) / total_ply AS colour_per
#             FROM `tabProduction Design Portion`
#             WHERE color_name LIKE %s
#             AND parent = %s
#             ORDER BY idx
#         """, (design_import_name, '%+%', design_import_name), as_dict=1)

#         return {"success": True, "color_data": color_data}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Design Parameters Error")
#         return {"success": False, "message": str(e)}


# def lookup_misc_remark_by_key(key):
#     """
#     Safe lookup in MiscellaneousMst by name or value — returns remark as float if possible, else None.
#     """
#     try:
#         if not key:
#             return None
#         row = frappe.db.sql("""
#             SELECT remark
#             FROM `tabMiscellaneousMst`
#             WHERE (name = %s OR value = %s)
#             LIMIT 1
#         """, (key, key), as_dict=1)
#         if row and row[0].get("remark") not in (None, ""):
#             try:
#                 return float(row[0]["remark"])
#             except:
#                 # remark exists but non-numeric
#                 return None
#         return None
#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "lookup_misc_remark_by_key Error")
#         return None


# @frappe.whitelist()
# def get_cut_loop_value(match_item):
#     """Return numeric remark for CUT_LOOP where MiscellaneousMst.value/name matches match_item."""
#     try:
#         if not match_item:
#             return 0.0
#         # use trantype join for CUT_LOOP (if present)
#         row = frappe.db.sql("""
#             SELECT m.remark
#             FROM `tabMiscellaneousMst` m
#             LEFT JOIN `tabTrantypeMst` t ON m.trantype = t.name
#             WHERE t.trantypename = 'CUT_LOOP'
#             AND (m.value = %s OR m.name = %s)
#             LIMIT 1
#         """, (match_item, match_item), as_dict=1)

#         if row and row[0].get("remark") not in (None, ""):
#             try:
#                 return float(row[0]["remark"])
#             except:
#                 return 0.0
#         # fallback: try generic lookup by key
#         val = lookup_misc_remark_by_key(match_item)
#         return float(val) if val is not None else 0.0
#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Get Cut Loop Value Error")
#         return 0.0


# @frappe.whitelist()
# def get_raw_material_value(raw_material_name):
#     """
#     Return numeric remark for raw material lookup.
#     First try trantype 'RAW MATERIAL TYPE', then fallback to generic lookup.
#     """
#     try:
#         if not raw_material_name:
#             return 0.0

#         row = frappe.db.sql("""
#             SELECT m.remark
#             FROM `tabMiscellaneousMst` m
#             WHERE (m.value = %s OR m.name = %s)
#             AND m.trantype = (
#                 SELECT name FROM `tabTrantypeMst` WHERE trantypename = 'RAW MATERIAL TYPE' LIMIT 1
#             )
#             LIMIT 1
#         """, (raw_material_name, raw_material_name), as_dict=1)

#         if row and row[0].get("remark") not in (None, ""):
#             try:
#                 return float(row[0]["remark"])
#             except:
#                 return 0.0

#         # fallback generic
#         val = lookup_misc_remark_by_key(raw_material_name)
#         return float(val) if val is not None else 0.0
#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Get Raw Material Value Error")
#         return 0.0


# @frappe.whitelist()
# def get_item_parameters(item_code):
#     """
#     Read AREA, PILEHEIGHT and Design Import from child table `tabItem Parameter`.
#     If stored value is an id referencing MiscellaneousMst, resolve remark from MiscellaneousMst.
#     Returns dict { area, pileheight, design_import }.
#     """
#     try:
#         if not item_code:
#             return {'area': 0.0, 'pileheight': 0.0, 'design_import': None}

#         rows = frappe.db.sql("""
#             SELECT parameter, value
#             FROM `tabItem Parameter`
#             WHERE parent = %s
#         """, (item_code,), as_dict=1)

#         res = {'area': 0.0, 'pileheight': 0.0, 'design_import': None}

#         if not rows:
#             return res

#         for r in rows:
#             param = str(r.get('parameter') or '').strip().upper()
#             raw_val = r.get('value')

#             # if raw_val is already numeric, use directly; else try to resolve from MiscellaneousMst
#             numeric_val = None
#             if raw_val is not None:
#                 # try convert directly
#                 try:
#                     numeric_val = float(raw_val)
#                 except:
#                     numeric_val = None

#             # if numeric conversion failed, attempt to lookup remark in MiscellaneousMst
#             if numeric_val is None and raw_val not in (None, ''):
#                 misc_lookup = lookup_misc_remark_by_key(str(raw_val).strip())
#                 if misc_lookup is not None:
#                     numeric_val = float(misc_lookup)

#             if param == 'AREA':
#                 res['area'] = numeric_val if numeric_val is not None else 0.0
#             elif param in ('PILEHEIGHT', 'PILE HEIGHT'):
#                 res['pileheight'] = numeric_val if numeric_val is not None else 0.0
#             elif param in ('DESIGN IMPORT', 'DESIGN_IMPORT', 'DESIGN'):
#                 # design import value probably stored as docname — keep raw string
#                 res['design_import'] = str(raw_val).strip() if raw_val not in (None, '') else None

#         return res
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Item Parameters Error")
#         return {'area': 0.0, 'pileheight': 0.0, 'design_import': None}


# def calculate_cat_ae_value(category, pileheight, ply, cut_loop_value, twistnontwist):
#     """
#     Category calculation (wastage fixed 0.07). Same logic as your MySQL function.
#     """
#     wastage = 0.07
#     base_calc = (pileheight + 4) * ply * 0.036 * (0 + cut_loop_value + 0 + 0 + wastage)

#     category_percentages = {
#         'Cat_A': 0,
#         'Cat_B': 3.85,
#         'Cat_C': 7.70,
#         'Cat_D': 11.54,
#         'Cat_E': 15.38
#     }
#     percentage = category_percentages.get(category, 0)

#     if twistnontwist in ('NonTwist', 'Non Twist', 0, '0', None):
#         if percentage == 0:
#             return base_calc
#         return (base_calc * percentage / 100.0) + base_calc
#     else:
#         base_with_tw = base_calc + 0.31
#         if percentage == 0:
#             return base_with_tw
#         return (base_with_tw * percentage / 100.0) + base_with_tw


# @frappe.whitelist()
# def calculate_lagat(item_code, category):
#     """
#     Main function: fetch item parameters (AREA, PILEHEIGHT, DESIGN IMPORT),
#     get design color rows, compute per-color lagat using misc lookups.
#     """
#     try:
#         if not item_code:
#             return {"success": False, "message": "Missing item_code"}

#         params = get_item_parameters(item_code)
#         area = params.get('area', 0.0)
#         pileheight = params.get('pileheight', 0.0)
#         design_import = params.get('design_import')

#         if not design_import:
#             return {"success": False, "message": "Design Import not found for this item"}

#         if area == 0 or pileheight == 0:
#             # give clear debug so user can see if lookup failed
#             return {"success": False, "message": f"AREA or PILEHEIGHT not found. Area: {area}, PileHeight: {pileheight}"}

#         design_data = get_design_parameters(design_import)
#         if not design_data.get("success"):
#             return design_data

#         color_rows = design_data.get("color_data") or []
#         if not color_rows:
#             return {"success": False, "message": f"No color data found for Design Import: {design_import}"}

#         details = []
#         total_lagat = 0.0

#         for row in color_rows:
#             # safe numeric conversions
#             try:
#                 ply = float(row.get("color_ply") or 0)
#             except:
#                 ply = 0.0

#             try:
#                 design_per = float(row.get("colour_per") or 0)
#             except:
#                 design_per = 0.0

#             raw_material = row.get("raw_material")
#             raw_material_multiplier = get_raw_material_value(raw_material)
#             cut_loop_value = get_cut_loop_value(row.get("match_item"))

#             cat_ae_value = calculate_cat_ae_value(
#                 category,
#                 pileheight,
#                 ply,
#                 cut_loop_value,
#                 row.get("twist_non_twist")
#             )

#             # final lagat formula
#             lagat = 0.0
#             if ply != 0:
#                 try:
#                     lagat = ((cat_ae_value * ply / ply) * area * design_per / 100.0 * raw_material_multiplier) / area
#                 except:
#                     lagat = 0.0
#             else:
#                 lagat = 0.0

#             details.append({
#                 "color_name": row.get("color_part"),
#                 "raw_material": raw_material,
#                 "ply": ply,
#                 "design_per": design_per,
#                 "cut_loop_value": cut_loop_value,
#                 "raw_material_value": raw_material_multiplier,
#                 "cat_ae_value": cat_ae_value,
#                 "lagat": lagat
#             })
#             total_lagat += lagat

#         return {
#             "success": True,
#             "total_lagat": total_lagat,
#             "details": details,
#             "parameters": {
#                 "area": area,
#                 "pileheight": pileheight,
#                 "category": category,
#                 "design_import": design_import
#             }
#         }
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Calculate Lagat Error")
#         return {"success": False, "message": str(e)}


import frappe

@frappe.whitelist()
def calculate_lagat(design_no, category):
    try:
        # Log incoming parameters
        frappe.logger().info(f"Calculating Lagat for Design: {design_no}, Category: {category}")

        # Mapping TranType IDs to parameter names
        trantype_map = {
            "TM-10-2025-00063": "pile_height",
            "TM-10-2025-00068": "area",
            "TM-10-2025-00062": "raw_material",
            "TM-09-2025-00049": "cut_loop"
        }

        # Fetch parameter values from MiscellaneousMst
        params = {}
        for trantype_id, param_name in trantype_map.items():
            val = frappe.db.get_value("MiscellaneousMst", {"trantype": trantype_id}, "value")
            params[param_name] = val or 0

        frappe.logger().info(f"Fetched Params: {params}")

        # Fetch Production Design Portion (colors, etc.)
        portions = frappe.db.sql("""
            SELECT 
                color_name, pile, loop_height, weight
            FROM `tabProduction Design Portion`
            WHERE parent = %s
        """, (design_no,), as_dict=True)

        results = []
        for portion in portions:
            color = portion.color_name
            pile = portion.pile or 0
            loop_height = portion.loop_height or 0
            weight = portion.weight or 0

            # Calculation logic
            lagat = (
                float(params["area"]) * 
                (float(params["pile_height"]) + float(loop_height)) * 
                float(params["raw_material"]) * 
                0.001
            )

            results.append({
                "color": color,
                "lagat": round(lagat, 2)
            })

        frappe.logger().info(f"Lagat Results: {results}")
        return {"status": "success", "data": results}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Lagat Calculation Error")
        return {"status": "error", "message": str(e)}
