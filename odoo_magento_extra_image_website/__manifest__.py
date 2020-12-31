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
    'name': 'MOB Extra Image Extension',
    'version': '1.0.0',
    'summary': 'Extra Image Extension',
    'author': 'Webkul Software Pvt. Ltd',
    'description': """
MOB Extra Image Extension
-------------------------

    Add An Extra Image tab inside product view.
    It'll sync all Magento Product Images inside Odoo
    Product Extra images and Vice Versa.

    """,
    'category': 'Generic Modules',
    'sequence': 1,
    'depends': [
                'odoo_magento_connect',
                'website_sale',
                'bridge_extra_image'
    ],
    'data': [
        # 'data/data_image_type.xml',
        'security/ir.model.access.csv',
        'views/mob_extra_image_view.xml'
        # 'views/mob_views.xml'
        # 'views/product_template_views.xml',
        # 'views/product_views.xml'
    ],
    'installable': True,
    'active': False,
    "pre_init_hook": "pre_init_check",
}
