"""
Configuration for docs
"""

def get_context(context):
	context.brand_html = "Church Management"
	context.source_link = "https://github.com/yourusername/church_management"
	context.docs_base_url = "https://yourusername.github.io/church_management"
	context.headline = "Church Management System Documentation"
	context.sub_heading = "A comprehensive church management system built on Frappe Framework"
	context.docs_footer = "Built with ❤️ using Frappe Framework"

	context.top_bar_items = [
		{"label": "Features", "url": context.docs_base_url + "/features"},
		{"label": "User Guide", "url": context.docs_base_url + "/user-guide"},
		{"label": "API", "url": context.docs_base_url + "/api"},
	]

	context.metatags = {
		"description": "A comprehensive church management system for managing members, services, events, small groups, and more.",
		"keywords": "church management, frappe, erp, open source"
	}

	context.introduction = """
	<div class="section" style="padding: 20px 0;">
		<div class="container">
			<h2>Welcome to Church Management System</h2>
			<p>A complete solution for managing your church operations including:</p>
			<ul>
				<li>Member Management</li>
				<li>Service Planning</li>
				<li>Event Management</li>
				<li>Small Groups</li>
				<li>Attendance Tracking</li>
				<li>Financial Management</li>
				<li>Asset Management</li>
			</ul>
		</div>
	</div>
	"""
