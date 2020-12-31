# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models
from ..core.res_partner import _unescape

class ProductCategory(models.Model):
    _inherit = "product.category"

    connector_mapping_ids = fields.One2many(
        string='Ecomm Channel Mappings',
        comodel_name='connector.category.mapping',
        inverse_name='name',
        copy=False
    )

    def write(self, vals):
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in dict(self._context or {}) for key in ecomm_cannels):
            if vals.get('name'):
                vals['name'] = _unescape(vals['name'])
        else:
            for cat_obj in self:
                cat_obj.connector_mapping_ids.need_sync = "Yes"
        return super(ProductCategory, self).write(vals)

