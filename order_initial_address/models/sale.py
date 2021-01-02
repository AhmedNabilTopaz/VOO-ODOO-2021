# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_address = fields.Text(
        string='Customer Address',
        default='',
        copy=False,
        readonly=True,
        help="Customer Address user in sale order")
    customer_billing_address = fields.Text(
        string='Billing Address',
        default='',
        copy=False,
        readonly=True,
        help="Customer Billing Address user in sale order")
    customer_shipping_address = fields.Text(
        string='Shipping Address',
        default='',
        copy=False,
        readonly=True,
        help="Customer Shipping Address user in sale order")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.updateOrderInitialAddress()
        return res

    def updateOrderInitialAddress(self):
        self.customer_address = self.getAddress(self.partner_id)
        self.customer_shipping_address = self.getAddress(self.partner_shipping_id)
        self.customer_billing_address = self.getAddress(self.partner_invoice_id)
        return True

    def getAddress(self, partner):
        address = ""
        companyName = partner.company_name
        if companyName:
            address = companyName
        name = partner.name
        if name:
            if address:
                address = "{}, {}".format(address, name)
            else:
                address = name
        address = self.getFormattedAddress(partner.street, address)
        address = self.getFormattedAddress(partner.street2, address)
        city = partner.city
        zip = partner.zip
        if city:
            if zip:
                city = "{} {}".format(city, zip)
        else:
            if zip:
                city = zip
        address = self.getFormattedAddress(city, address)
        stateObj = partner.state_id
        if stateObj:
            state = "{} {}".format(stateObj.name, stateObj.code)
            address = self.getFormattedAddress(state, address)
        address = self.getFormattedAddress(partner.country_id.name, address)
        return address

    def getFormattedAddress(self, field, address):
        if field:
            if address:
                address = "{}\n{}".format(address, field)
            else:
                address = field
        return address

    def update_initial_address(self):
        orderIds = self._context.get('active_ids')
        orderObjs = self.search([('id', 'in', orderIds), ('customer_address', '=', '')])
        for orderObj in orderObjs:
            orderObj.updateOrderInitialAddress()
        text = "Initial address of {} order(s) have been successfully updated.".format(len(orderObjs))
        return self.env['wk.wizard.message'].genrated_message(text)
