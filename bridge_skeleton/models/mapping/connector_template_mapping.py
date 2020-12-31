# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, api, models


class ConnectorTemplateMapping(models.Model):
    _name = "connector.template.mapping"
    _inherit = ['connector.common.mapping']
    _order = 'id desc'
    _description = "Ecomm Product Template"

    name = fields.Many2one('product.template', string='Template Name')
    is_variants = fields.Boolean(string='Is Variants')

    @api.model
    def create_template_mapping(self, data):
        if data.get('odoo_id'):
            ctx = dict(self._context or {})
            template_obj = self.env['product.product'].browse(
                data.get('odoo_id')).product_tmpl_id
            if not template_obj.attribute_line_ids :
                odooMapDict = {
                    'name' : template_obj.id,
                    'odoo_id' : template_obj.id,
                    'ecomm_id' : data.get('ecomm_id'),
                    'instance_id' : ctx.get('instance_id'),
                    'created_by' : 'Manual Mapping'
                }
                res = self.create(odooMapDict)
        return True

    @api.model
    def create_n_update_attribute_line(self, data):
        line_dict = {}
        if data.get('product_tmpl_id'):
            template_id = data.get('product_tmpl_id', 0)
            attribute_id = data.get('attribute_id', 0)
            domain = [('product_tmpl_id', '=', template_id)]
            if 'values' in data:
                value_ids = []
                price_val_dict = {}
                for value in data.get('values', {}):
                    value_id = value.get('value_id', 0)
                    value_ids.append(value_id)
                    price_val_dict[value_id] = value.get('price_extra', 0.0)
                line_dict['value_ids'] = [(6, 0, value_ids)]
            search_domain = domain + [('attribute_id', '=', attribute_id)]
            prod_attr_line_model = self.env['product.template.attribute.line']
            exist_attr_line_objs = prod_attr_line_model.search(search_domain)
            if exist_attr_line_objs:
                for exist_attr_line_obj in exist_attr_line_objs:
                    exist_attr_line_obj.write(line_dict)
            else:
                line_dict.update({
                    'attribute_id' : attribute_id,
                    'product_tmpl_id' : template_id
                })
                attribute_line_obj = prod_attr_line_model.create(line_dict)
                for valueObj in attribute_line_obj.product_template_value_ids:
                    valueObj.price_extra = price_val_dict.get(valueObj.product_attribute_value_id.id, 0.0)
            return True
        return False
