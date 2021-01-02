# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

class ProductionLot(models.Model):
    _inherit = "stock.production.lot"
    
    cost_price = fields.Float(string='Cost Price', help="Cost Stock Move Line")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product_id = vals['product_id']
            lot_num = vals['name']
            move_line_objs = self.env['stock.move.line'].search([('lot_name', '=',lot_num), ('product_id', '=',product_id)], limit=1)
            if move_line_objs:
                if move_line_objs.move_id and move_line_objs.move_id.picking_id and move_line_objs.move_id.picking_id.purchase_id:
                   vals['cost_price'] = move_line_objs.cost_price
        return super(ProductionLot, self).create(vals_list)