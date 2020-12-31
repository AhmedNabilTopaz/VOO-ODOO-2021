# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models


class ConnectorExtraCategory(models.Model):
    _name = "connector.extra.category"
    _order = 'id desc'
    _description = "Connector Extra Category"

    instance_id = fields.Many2one(
        'connector.instance', string='Connector Instance')
    ecommerce_channel = fields.Selection(
        related="instance_id.ecomm_type", 
        string="eCommerce Channel", store=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', auto_join=True, index=True, ondelete="cascade")
    product_id = fields.Many2one('product.product', 'Product Product', auto_join=True, index=True, ondelete="cascade")
    categ_ids = fields.Many2many(
        'product.category',
        'product_categ_rel',
        'product_id',
        'categ_id',
        string='Extra Categories')
