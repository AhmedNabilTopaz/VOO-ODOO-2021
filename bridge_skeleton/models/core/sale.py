# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    @api.depends('picking_ids', 'order_line.qty_delivered')
    def _shipped_status_compute(self):
        for sale_obj in self:
            sale_obj.is_shipped = all(
                line.qty_delivered >= line.product_uom_qty
                for line in sale_obj.order_line.filtered(lambda l: l.product_id.type != 'service')
            )

    def _invoiced_status_compute(self):
        for sale_obj in self:
            sale_obj.is_invoiced = True if all(invoice_id.state == 'posted' for invoice_id in sale_obj.invoice_ids) else False

    _ecommerce_selection = lambda self, * \
        args, **kwargs: self.env['connector.snippet']._get_ecomm_extensions(*args, **kwargs)

    ecommerce_channel = fields.Selection(
        selection='_ecommerce_selection',
        string='eCommerce Channel',
        help="Name of ecommerce from where this Order is generated.")
    is_shipped = fields.Boolean(compute='_shipped_status_compute')
    is_invoiced = fields.Boolean(compute='_invoiced_status_compute')

    def action_cancel(self):
        self.skeleton_pre_order_cancel()
        res = super(SaleOrder, self).action_cancel()
        self.skeleton_post_order_cancel(res)
        return res

    def skeleton_pre_order_cancel(self):
        return True

    def skeleton_post_order_cancel(self, result):
        ctx = dict(self._context or {})
        snippet_obj = self.env['connector.snippet']
        ecomm_cannels = dict(snippet_obj._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            return True
        for sale_order in self:
            if sale_order.ecommerce_channel in ecomm_cannels:
                for ecomm in ecomm_cannels:
                    snippet_obj.manual_connector_order_operation('cancel', ecomm, sale_order)
