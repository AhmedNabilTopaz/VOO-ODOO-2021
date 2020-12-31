# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import _, fields, models

class MobImageType(models.Model):
    _name = 'connector.product.image.type'
    _description = 'Connector Product Image Type'

    name = fields.Char(string='Type')
    label = fields.Char(string='Label', size=100)

class MobExtraImage(models.Model):
    _inherit = "connector.extra.image"

    extra_image_id = fields.Integer(string='Magento Image Id', readonly= True)
    magento_product_id = fields.Integer(string='Magento Product Id', default=0,  readonly= True)
    magento_image_type = fields.Many2many(
        'connector.product.image.type', string='Image Type')