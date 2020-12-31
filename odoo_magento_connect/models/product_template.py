# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    prod_type = fields.Char(string='Magento Type')
    attribute_set_id = fields.Many2one(
        'magento.attribute.set',
        string='Magento Attribute Set',
        help="Magento Attribute Set, Used during configurable product generation at Magento.")
