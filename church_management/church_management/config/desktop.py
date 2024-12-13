from frappe import _

def get_data():
	return [
		{
			"module_name": "Church Management",
			"color": "blue",
			"icon": "octicon octicon-organization",
			"type": "module",
			"label": _("Church Management"),
			"items": [
				{
					"type": "doctype",
					"name": "Church Member",
					"label": _("Members"),
					"description": _("Manage church members"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Family Unit",
					"label": _("Family Units"),
					"description": _("Manage family units"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Church Service",
					"label": _("Services"),
					"description": _("Manage church services"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Church Event",
					"label": _("Events"),
					"description": _("Manage church events"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Church Small Group",
					"label": _("Small Groups"),
					"description": _("Manage small groups"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Church Attendance",
					"label": _("Attendance"),
					"description": _("Track attendance"),
				},
				{
					"type": "doctype",
					"name": "Church Donation",
					"label": _("Donations"),
					"description": _("Manage donations"),
				},
				{
					"type": "doctype",
					"name": "Church Asset",
					"label": _("Assets"),
					"description": _("Manage church assets"),
				},
				{
					"type": "doctype",
					"name": "Church Settings",
					"label": _("Settings"),
					"description": _("Configure church settings"),
				}
			]
		}
	]
