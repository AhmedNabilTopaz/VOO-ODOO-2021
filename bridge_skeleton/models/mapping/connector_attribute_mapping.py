# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models

class ConnectorAttributeMapping(models.Model):
    _name = "connector.attribute.mapping"
    _inherit = ['connector.common.mapping']
    _order = 'id desc'
    _description = "Ecomm Product Attribute"

    name = fields.Many2one('product.attribute', string='Product Attribute')
    ecomm_attribute_code = fields.Char(string="Ecomm Attribute Code")
