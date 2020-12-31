# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models


def _unescape(text):
    ##
    # Replaces all encoded characters by urlib with plain utf8 string.
    #
    # @param text source text.
    # @return The plain text.
    from urllib.parse import unquote_plus
    try:
        text = unquote_plus(text)
        return text
    except Exception as e:
        return text


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            vals = self.customer_array(vals)
        return super().create(vals)

    def write(self, vals):
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            vals = self.customer_array(vals)
        return super().write(vals)

    def customer_array(self, data):
        dic = {}
        stateModel = self.env['res.country.state']
        country_code = data.pop('country_code', False)
        region = data.pop('region', False)
        if country_code:
            countryObj = self.env['res.country'].search(
                [('code', '=', country_code)], limit=1)
            if countryObj:
                data['country_id'] = countryObj.id
                if region:
                    region = _unescape(region)
                    stateObj = stateModel.search([
                        ('name', '=', region),
                        ('country_id', '=', countryObj.id)
                    ], limit=1)
                    if stateObj:
                        data['state_id'] = stateObj.id
                    else:
                        dic['name'] = region
                        dic['country_id'] = countryObj.id
                        code = region[:3].upper()
                        temp = code
                        stateObj = stateModel.search(
                            [('code', '=ilike', code)], limit=1)
                        counter = 0
                        while stateObj and counter < 100:
                            code = temp + str(counter)
                            stateObj = stateModel.search(
                                [('code', '=ilike', code)], limit=1)
                            counter = counter + 1
                        if counter == 100:
                            code = region.upper()
                        dic['code'] = code
                        stateObj = stateModel.create(dic)
                        data['state_id'] = stateObj.id
        tag = data.pop('tag', False)
        if tag:
            tag = _unescape(tag)
            tag_objs = self.env['res.partner.category'].search(
                [('name', '=', tag)], limit=1)
            if not tag_objs:
                tagId = self.env['res.partner.category'].create({'name': tag})
            else:
                tagId = tag_objs[0].id
            data['category_id'] = [(6, 0, [tagId])]
        data.pop('ecomm_id', None)
        if data.get('wk_company'):
            data['wk_company'] = _unescape(data['wk_company'])
        if data.get('name'):
            data['name'] = _unescape(data['name'])
        if data.get('email'):
            data['email'] = _unescape(data['email'])
        if data.get('street'):
            data['street'] = _unescape(data['street'])
        if data.get('street2'):
            data['street2'] = _unescape(data['street2'])
        if data.get('city'):
            data['city'] = _unescape(data['city'])
        return data

    def _handle_first_contact_creation(self):
        """ On creation of first contact for a company (or root) that has no address, assume contact address
        was meant to be company address """
        parent = self.parent_id
        address_fields = self._address_fields()
        if parent and (
            parent.is_company or not parent.parent_id) and len(
            parent.child_ids) == 1 and any(
            self[f] for f in address_fields) and not any(
                parent[f] for f in address_fields):
            addr_vals = self._update_fields_values(address_fields)
            parent.update_address(addr_vals)

    wk_company = fields.Char(string='Ecomm Company', size=128)
