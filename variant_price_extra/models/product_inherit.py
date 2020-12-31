# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('product_template_attribute_value_ids.price_extra')
    def _compute_product_price_extra(self):
        result = {}
        for product in self:
            price_extra =sum(product.mapped('product_template_attribute_value_ids.price_extra'))
            product.price_extra = price_extra + product.wk_extra_price
            product.attr_price_extra = price_extra

    wk_extra_price = fields.Float('Price Extra')
    price_extra = fields.Float(
        'Variant Price Extra', compute='_compute_product_price_extra',
        digits='Product Price',
        help="This is the sum of the extra price of all attributes")

    attr_price_extra = fields.Float(compute='_compute_product_price_extra',
                                    string='Variant Extra Price', digits='Product Price')
