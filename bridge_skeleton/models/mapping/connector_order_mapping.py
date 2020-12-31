# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

class ConnectorOrderMapping(models.Model):
    _name = "connector.order.mapping"
    _order = 'id desc'
    _description = "Ecomm Orders"

    name = fields.Char(string='eCommerce Order Ref.')
    odoo_order_id = fields.Many2one(
        'sale.order', string='ODOO Order Id', required=1)
    ecommerce_channel = fields.Selection(
        related="odoo_order_id.ecommerce_channel", 
        string="eCommerce Channel", store=True)
    ecommerce_order_id = fields.Integer(
        string='eCommerce Order Id', required=1)
    instance_id = fields.Many2one(
        'connector.instance', string='Connector Instance')
    order_status = fields.Selection(
        related="odoo_order_id.state", string="Order Status")
    is_invoiced = fields.Boolean(
        related="odoo_order_id.is_invoiced", string="Paid")
    is_shipped = fields.Boolean(
        related="odoo_order_id.is_shipped", string="Shipped")


    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        if ctx.get('instance_id'):
            vals['instance_id'] = ctx.get('instance_id')
        return super(ConnectorOrderMapping, self).create(vals)