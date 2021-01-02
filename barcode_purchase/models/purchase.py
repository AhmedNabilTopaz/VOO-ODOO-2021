# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search(
            ['|',('barcode', '=', barcode),('default_code', '=', barcode)]
            , limit=1)
        if product:
            order_lines = self.order_line.filtered(
                lambda r: r.product_id == product)
            if order_lines:
                order_line = order_lines[0]
                qty = order_line.product_qty
                order_line.product_qty = qty + 1
            else:
                newId = self.order_line.new({
                    'product_id': product.id,
                    'product_qty': 1,
                    'price_unit': product.lst_price
                })
                self.order_line += newId
                newId.onchange_product_id()
        else:
            raise UserError(
                _('Scanned barcode %s is not related to any product.') %
                barcode)
