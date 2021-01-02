# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self,vals):
        data = self.getTrackDetails(vals)
        res = super().write(vals)
        self.addTrackingMsg(data)
        return res

    @api.depends('user_id')
    def _get_user(self):
        user = self._uid
        for obj in self:
            if obj.user_id and obj.user_id.id == user:
                obj.is_user = False
            else:
                obj.is_user = True
    
    magento_order_status = fields.Char(string='Magento Order Status', help="Status of Magento Orders")
    magento_payment_method = fields.Char(string='Payment Method', help="Payment Method of Magento Orders")
    billing_latitude = fields.Float(string='Latitude', digits=(16, 5))
    billing_longitude = fields.Float(string='Longitude', digits=(16, 5))
    shipping_latitude = fields.Float(string='Latitude', digits=(16, 5))
    shipping_longitude = fields.Float(string='Longitude', digits=(16, 5))
    magento_delivery_note = fields.Text(string='Delivery Note')
    is_user = fields.Boolean('Current User', compute=_get_user, store='1')


    def action_confirm(self):
        date_order = self.date_order
        res = super(SaleOrder, self).action_confirm()
        if date_order:
            ship_address = self.partner_shipping_id
            invoice_address = self.partner_invoice_id
            self.write({
                'date_order':date_order,
                'billing_latitude':invoice_address.partner_latitude,
                'billing_longitude':invoice_address.partner_longitude,
                'shipping_latitude':ship_address.partner_latitude,
                'shipping_longitude':ship_address.partner_longitude
            })
        return res
    
    def set_salesperson(self):
        self.user_id = self.env.uid
        return True

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _update_line_quantity(self, values):
        orders = self.mapped('order_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.order_id == order)
            msg = "<b>" + _("The ordered quantity has been updated.") + "</b><ul>"
            for line in order_lines:
                msg += "<li> %s:" % (line.product_id.display_name,)
                msg += "<br/>" + _("Ordered Quantity") + ": %s -> %s <br/>" % (
                line.product_uom_qty, float(values['product_uom_qty']),)
                if line.product_id.type in ('consu', 'product'):
                    msg += _("Delivered Quantity") + ": %s <br/>" % (line.qty_delivered,)
                msg += _("Invoiced Quantity") + ": %s <br/>" % (line.qty_invoiced,)
                msg += _("Unit Price") + ": %s -> %s <br/>" % (
                line.price_unit, float(values['price_unit']),)
            msg += "</ul>"
            order.message_post(body=msg)