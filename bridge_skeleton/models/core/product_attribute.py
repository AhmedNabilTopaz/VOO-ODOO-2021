# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    @api.model
    def check_attribute(self, vals):
        if vals.get('name'):
            attribute_obj = self.search(
                [('name', '=ilike', vals['name'])], limit=1)
            return attribute_obj
        return False

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            attribute_obj = self.check_attribute(vals)
            if attribute_obj:
                return attribute_obj
        return super(ProductAttribute, self).create(vals)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            attribute_value_objs = self.search([('name', '=', vals.get(
                'name')), ('attribute_id', '=', vals.get('attribute_id'))])
            if attribute_value_objs:
                return attribute_value_objs[0]
        return super(ProductAttributeValue, self).create(vals)