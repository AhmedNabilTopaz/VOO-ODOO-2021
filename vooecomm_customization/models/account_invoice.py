# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.move"

    magento_payment_method = fields.Char(string='Payment Method', help="Payment Method of Magento Orders")

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if vals.get('type') == 'out_invoice' and vals.get('invoice_origin'):
            order = self.env['sale.order'].sudo().search(
                [('name', '=', vals.get('invoice_origin'))],
                limit=1,
            )
            if order:
                res.magento_payment_method = order.magento_payment_method
        return res
