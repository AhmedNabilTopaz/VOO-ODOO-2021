# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models
from ..core.res_partner import _unescape


class ConnectorCategoryMapping(models.Model):
    _name = "connector.category.mapping"
    _inherit = ['connector.common.mapping']
    _order = 'id desc'
    _description = "Ecomm Category"

    name = fields.Many2one('product.category', string='Category Name')

    @api.model
    def create_category(self, data):
        """Create and update a category by any webservice like xmlrpc.
        @param data: details of category fields in list.
        """
        categ_dict = {}
        if data.get('name'):
            categ_dict['name'] = _unescape(data.get('name'))

        if data.get('type'):
            categ_dict['type'] = data.get('type')
        if data.get('parent_id'):
            categ_dict['parent_id'] = data.get('parent_id')
        if data.get('method') == 'create':
            ecomm_id = data.get('ecomm_id')
            categoryObj = self.env['product.category'].create(categ_dict)
            odooMapVals = {
                'name' : categoryObj.id,
                'odoo_id' : categoryObj.id,
                'ecomm_id' : ecomm_id,
                'instance_id' : self._context.get('instance_id'),
                'created_by' : self._context.get('created_by')
            }
            self.create(odooMapVals)
            return categoryObj.id
        elif data.get('method') == 'write':
            categoryObj = self.env['product.category'].browse(data.get('category_id')).write(categ_dict)
            return True
        return False
