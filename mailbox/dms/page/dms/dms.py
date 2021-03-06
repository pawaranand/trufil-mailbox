from __future__ import unicode_literals
import frappe
""""
		if dms:
			[{"value":"modules","expandable":1},{"Misc. Attachments","expandable":1}]
		elif mudules:
			get all mudules defined in DMS Config in sorted manner
			[{"value":"selling","expandable":1},{"buying","expandable":1}]
		elif given in [is_single]:
			get folders first and then files
			[{"value":"Folder Name","expandable":1},{"file_name","expandable":0}]
		elif given in [is_group doctype]:
			get all docnames
			[{"value":"docname","expandable":1},{"docname","expandable":1}]
		elif given in DMS Config as folder:
			get all files against folder
			[{"value":"file_name","expandable":0},{"file_name","expandable":0}]
		else:
			get all files under docname
			[{"value":"file_name","expandable":0},{"file_name","expandable":0}]

	"""
modules = [] 	
doctypes = []
folders = []
single_type = []
docnames = []

@frappe.whitelist()
def get_children():
	args = frappe.local.form_dict
	response = []
	docn = {}
	

	if args.get('parent') == 'DMS':
		response = [{"value":"Modules","expandable":1}]
		single_types = frappe.db.sql("""Select name from `tabDMS` where is_single=1""",as_dict=1)
		[response.append({"value":d["name"],"expandable":1,"type":"single"}) for d in single_types]
		[single_type.append(d["name"]) for d in single_types]

	elif args.get('parent') == 'Modules':
		modules_list = frappe.db.sql("""Select parent_module from `tabDMS` where is_group=1""",as_dict=1)
		[response.append({"value":d["parent_module"],"expandable":1,"type":"module"}) for d in modules_list]
		[modules.append(d["parent_module"]) for d in modules_list]

	elif args.get('parent')	in modules:
		doctypes_list = frappe.db.sql("""Select doctype_name from `tabDMS` 
			where is_group=1 and parent_module='%s'"""%args.get('parent'),as_dict=1)	
		[response.append({"value":d["doctype_name"],"expandable":1}) for d in doctypes_list]
		[doctypes.append(d["doctype_name"]) for d in doctypes_list]

	elif args.get('parent')	in doctypes:
		docnames_list = frappe.get_list(args.get('parent'),fields=["name"])
		[response.append({"value":d["name"],"expandable":1,"type":"doc"}) for d in docnames_list]
		[docnames.append({d["name"]:args.get('parent')}) for d in docnames_list]

	elif args.get('parent')	in single_type:
		folders_list = frappe.db.sql("""Select folder_name from `tabDMS` 
			where parent='%s'"""%args.get('parent'),as_dict=1)
		[response.append({"value":d["folders_name"],"expandable":1,"folder":1}) for d in folders_list]
		[folders.append(d["folder_name"]) for d in folders_list]
		attachments = frappe.get_all("File Data", fields=["name", "file_name", "file_url"],
				filters = {"attached_to_doctype":args.get('parent')})
		[response.append({"value":d["file_name"],"expandable":0,"file":1,"file_url":d["file_url"]}) for d in attachments]

	elif args.get('parent')	in folders:
		attachments = frappe.get_all("File Data", fields=["name", "file_name", "file_url"],
				filters = {"attached_to_doctype":args.get('parent')})
		[response.append({"value":d["file_name"],"expandable":0,"file":1,"file_url":d["file_url"]}) for d in attachments]		

	
	else:
		attachments = frappe.get_all("File Data", fields=["name", "file_name", "file_url"],
				filters = {"attached_to_name":args.get('parent')})
		[response.append({"value":d["file_name"],"expandable":0,"file":1,"file_url":d["file_url"]}) for d in attachments]		

	return response	

@frappe.whitelist()
def add_node():
	ctype = frappe.form_dict.get('ctype')
	parent_field = 'parent_' + ctype.lower().replace(' ', '_')
	name_field = ctype.lower().replace(' ', '_') + '_name'

	doc = frappe.new_doc(ctype)
	doc.update({
		name_field: frappe.form_dict['name_field'],
		parent_field: frappe.form_dict['parent'],
		"is_group": frappe.form_dict['is_group']
	})
	if ctype == "Sales Person":
		doc.employee = frappe.form_dict.get('employee')

	doc.save()