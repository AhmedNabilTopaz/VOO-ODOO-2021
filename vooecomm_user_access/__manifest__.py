# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################
{
	'name': 'VooEcomm User Access',
	'summary': '''''',
	'description': '''''',

	'author': 'Webkul Software Pvt. Ltd.',
	'license': 'Other proprietary',
	'website': 'https://store.webkul.com/Odoo.html',

	'category': 'Sales Management',
	'version': '1.0.4',
	'depends': ['delivery_boy'],
	'data': [
		'security/security.xml',
		'security/ir.model.access.csv',

		'views/sale_order.xml',
		'views/stock_picking.xml',
		'views/stock_warehouse.xml',

		'wizard/select_delivery_boy.xml',
		'wizard/stock_backorder_confirmation.xml',
	],

	'pre_init_hook': 'pre_init_check',
	'sequence': 1,
}
