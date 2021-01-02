# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

{
    'name': 'VOO Ecomm Customization',
    'version': '1.0.0',
    'category': 'Generic Modules',
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'https://store.webkul.com',
    'sequence': 1,
    'summary': 'Basic Traccar Application',
    'description': """This module works very well with Odoo 13.0""",
    'depends': [
        'bridge_skeleton',
        'purchase_stock',
        'order_initial_address'
    ],
    'data': [
        'data/voo_ecom_server_actions.xml',
        'security/ir.model.access.csv',
        'wizard/salesperson_wizard_view.xml',
        'views/res_config_settings_views.xml',
        'views/stock_move_views.xml',
        'views/account_move_views.xml',
        'views/sale_views.xml',
        'views/stock_production_lot_views.xml',
        'views/connector_warehouse_mapping_views.xml',
        'views/product_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'pre_init_hook': 'pre_init_check',
}
