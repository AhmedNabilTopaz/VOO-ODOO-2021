# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

class Picking(models.Model):
    _inherit = "stock.picking"
    
    def button_validate(self):
        res = super(Picking, self).button_validate()
        purchase_obj = self.purchase_id
        if purchase_obj:
            line_data = []
            for move_obj in self.move_ids_without_package:
                if move_obj.move_line_nosuggest_ids:
                    product_obj = move_obj.product_id
                    product_id = product_obj.id
                    purchase_line_obj = purchase_obj.order_line.filtered(lambda obj: obj.product_id.id == product_id)
                    if purchase_line_obj and len(purchase_line_obj) == 1:
                        flag = True
                        product_uom, description = product_obj.uom_po_id or product_obj.uom_id, product_obj.display_name
                        date_planned = purchase_line_obj.date_planned if purchase_line_obj and purchase_line_obj.date_planned else purchase_obj.date_planned
                        taxes_ids = purchase_line_obj.taxes_id.ids
                        for move_line_obj in move_obj.move_line_nosuggest_ids:
                            lot_num = move_line_obj.lot_name if not move_line_obj.lot_id else move_line_obj.lot_id.name
                            cost_price, qty_done = move_line_obj.cost_price, move_line_obj.qty_done
                            if lot_num:
                                lot_objs = self.env['stock.production.lot'].search([('name', '=',lot_num), ('product_id', '=',product_id)], limit=1)
                                if lot_objs:
                                    lot_objs.cost_price = cost_price
                            if lot_num and qty_done and cost_price:
                                line_dict = {
                                    'product_id': product_id,
                                    'name': description,
                                    'product_uom': product_uom.id,
                                    'date_planned':date_planned,
                                    'product_qty':qty_done,
                                    'taxes_id': [(6, 0, taxes_ids)],
                                    'price_unit':cost_price
                                }
                                if flag:
                                    flag =False
                                    purchase_line_obj.price_unit = cost_price
                                    purchase_line_obj.product_qty = qty_done
                                else:
                                    line_data.append((0, 0, line_dict))
                    else:
                        for move_line_obj in move_obj.move_line_nosuggest_ids:
                            lot_num = move_line_obj.lot_name if not move_line_obj.lot_id else move_line_obj.lot_id.name
                            cost_price = move_line_obj.cost_price
                            if lot_num:
                                lot_objs = self.env['stock.production.lot'].search([('name', '=',lot_num), ('product_id', '=',product_id)], limit=1)
                                if lot_objs:
                                    lot_objs.cost_price = cost_price
            if line_data:
                purchase_obj.order_line = line_data
        return res

    def action_done(self):
        res = super().action_done()
        for pick in self:
            sale_orders = pick.sale_id
            if sale_orders:
                sale_orders._create_invoices(final=True)
        return res
