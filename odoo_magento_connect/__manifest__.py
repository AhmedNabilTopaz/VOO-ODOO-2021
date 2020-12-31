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
    'name': 'Magento Odoo Bridge',
    'version': '3.0.1',
    'category': 'Generic Modules',
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'https://store.webkul.com/Magento-2/Odoo-Bridge-For-Magento2.html',
    'sequence': 1,
    'summary': 'Basic MOB',
    'description': """

Magento Odoo Bridge (MOB)
=========================

This Brilliant Module will Connect Odoo with Magento and synchronise Data.
--------------------------------------------------------------------------


Some of the brilliant feature of the module:
--------------------------------------------

    1. synchronise all the catalog categories to Magento.

    2. synchronise all the catalog products to Magento.

    3. synchronise all the Attributes and Values.

    4. synchronise all the order(Invoice, shipping) Status to Magento.

    5. Import Magento Regions.

    6. synchronise inventory of catelog products.

This module works very well with latest version of magento 2.* and Odoo 13.0
------------------------------------------------------------------------------
    """,
    'depends': [
        'bridge_skeleton',
        'variant_price_extra',
    ],
    'data': [
        'wizard/magento_wizard_view.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/connector_instance_view.xml',
        'views/magento_attribute_set_view.xml',
        'views/connector_product_mapping_view.xml',
        'views/mob_menus.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
    'pre_init_hook': 'pre_init_check',
}
