# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


class account_payment(models.Model):
    _inherit = "account.payment"

    def post(self):
        self.skeleton_pre_payment_post()
        res = super().post()
        self.skeleton_after_payment_post(res)
        return res

    def skeleton_pre_payment_post(self):
        return True

    def get_ecomm_orders(self, invoice_objs):
        origins = invoice_objs.mapped('invoice_origin')
        sales_order = self.env['sale.order'].search[('name', 'in', origins)]
        return sales_order

    def skeleton_after_payment_post(self, result):
        ctx = dict(self._context or {})
        snippet_obj = self.env['connector.snippet']
        ecomm_cannels = dict(snippet_obj._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            return True
        for rec in self:
            origins = rec.invoice_ids.mapped('invoice_origin')
            sales_order = self.env['sale.order'].search([('name', 'in', origins)])
            for ecomm in ecomm_cannels:
                response = snippet_obj.manual_connector_order_operation('invoice', ecomm, sales_order)
        return True
