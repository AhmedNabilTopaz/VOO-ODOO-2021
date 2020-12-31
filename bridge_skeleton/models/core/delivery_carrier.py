# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models
from .res_partner import _unescape


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            vals['name'] = _unescape(vals['name'])
            prodObj = self.env['product.product'].create({
                'name' : vals['name'],
                'type' : 'service'
            })
            vals['product_id'] = prodObj.id
        return super().create(vals)
