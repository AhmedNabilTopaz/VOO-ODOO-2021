# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models


class MagentoAttributeSet(models.Model):
    _name = "magento.attribute.set"
    _description = "Magento Attribute Set"
    _order = 'id desc'

    name = fields.Char(string='Magento Attribute Set')
    attribute_ids = fields.Many2many(
        'product.attribute',
        'product_attr_set',
        'set_id',
        'attribute_id',
        string='Product Attributes',
        readonly=True,
        help="Magento Set attributes will be handle only at magento.")
    instance_id = fields.Many2one(
        'connector.instance', string='Magento Instance')
    ecommerce_channel = fields.Selection(
        related="instance_id.ecomm_type", 
        string="eCommerce Channel", store=True)
    set_id = fields.Integer(string='Magento Set Id', readonly=True)
    created_by = fields.Char(string='Created By', default="odoo", size=64)
    create_date = fields.Datetime(string='Created Date')
    write_date = fields.Datetime(string='Updated Date')

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        if ctx.get('instance_id'):
            vals['instance_id'] = ctx.get('instance_id')
        return super(MagentoAttributeSet, self).create(vals)
