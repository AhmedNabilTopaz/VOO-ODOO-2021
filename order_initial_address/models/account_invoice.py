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

    customer_address = fields.Text(
        string='Billing Address',
        default='',
        copy=False,
        readonly=True,
        help="Customer Address user in invoice")
    customer_shipping_address = fields.Text(
        string='Shipping Address',
        default='',
        copy=False,
        readonly=True,
        help="Customer Shipping Address user in invoice")

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if vals.get('type') == 'out_invoice':
            order = self.env['sale.order'].search(
                [('name', '=', vals.get('invoice_origin'))],
                limit=1,
            )
            if order:
                if order.customer_billing_address and order.customer_shipping_address:
                    address = {
                        'customer_address'         : order.customer_billing_address,
                        'customer_shipping_address': order.customer_shipping_address,
                    }
                else:
                    address = {
                        'customer_address'         : self.env['sale.order'].getAddress(res.partner_id),
                        'customer_shipping_address': self.env['sale.order'].getAddress(res.partner_shipping_id),
                    }
                res.write(address)
        return res


    def update_initial_address(self):
        invoiceIds = self._context.get('active_ids')
        invoiceObjs = self.search([('id', 'in', invoiceIds), ('customer_address', '=', '')])
        for invoiceObj in invoiceObjs:
            invoiceObj.customer_address = self.env['sale.order'].getAddress(invoiceObj.partner_id)
            invoiceObj.customer_shipping_address = self.env['sale.order'].getAddress(invoiceObj.partner_shipping_id)
        text = "Initial address of {} invoice(s) have been successfully updated.".format(len(invoiceObjs))
        return self.env['wk.wizard.message'].genrated_message(text)
