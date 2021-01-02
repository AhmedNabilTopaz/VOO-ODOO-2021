# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = "stock.picking"


    customer_shipping_address = fields.Text(
        string='Shipping Address',
        default='',
        copy=False,
        readonly=True,
        help="Inital Customer Shipping Address")

    @api.model
    def create(self, vals):
        res = super(Picking, self).create(vals)
        res.updateOrderInitialAddress()
        return res

    def action_confirm(self):
        res = super(Picking, self).action_confirm()
        for pickObj in self:
            if not pickObj.customer_shipping_address:
                pickObj.updateOrderInitialAddress()
        return res

    def button_validate(self):
        res = super(Picking, self).button_validate()
        for pickObj in self:
            if not pickObj.customer_shipping_address:
                pickObj.updateOrderInitialAddress()
        return res

    def updateOrderInitialAddress(self):
        self.customer_shipping_address = self.getAddress(self.partner_id)
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
        addrZip = partner.zip
        if city:
            if addrZip:
                city = "{} {}".format(city, addrZip)
        else:
            if addrZip:
                city = addrZip
        address = self.getFormattedAddress(city, address)
        stateObj = partner.state_id
        if stateObj:
            state = "{} {}".format(stateObj.name, stateObj.code)
            address = self.getFormattedAddress(state, address)
        address = self.getFormattedAddress(partner.country_id.name, address)
        if partner.phone:
            address = self.getFormattedAddress(partner.phone, address)
        return address

    def getFormattedAddress(self, field, address):
        if field:
            if address:
                address = "{}\n{}".format(address, field)
            else:
                address = field
        return address

    def update_initial_address(self):
        pickingIds = self._context.get('active_ids')
        pickObjs = self.search([('id', 'in', pickingIds), ('customer_shipping_address', '=', '')])
        for pickObj in pickObjs:
            pickObj.updateOrderInitialAddress()
        text = "Initial address of {} picking(s) have been successfully updated.".format(len(pickObjs))
        return self.env['wk.wizard.message'].genrated_message(text)
