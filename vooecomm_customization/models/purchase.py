# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    READONLY_STATES = {
        'purchase': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    def write(self,vals):
        data = self.getTrackDetails(vals)
        res = super(PurchaseOrder, self).write(vals)
        self.addTrackingMsg(data)
        return res

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError("You cannot change the type of a purchase order line. Instead you should delete the current line and create a new line of the proper type.")

        if 'price_unit' in values:
            orders = self.mapped('order_id')
            for order in orders:
                order_lines = self.filtered(lambda x: x.order_id == order)
                msg = "<b>" + _("The unit price has been updated.") + "</b><ul>"
                for line in order_lines:
                    msg += "<li> %s:" % (line.product_id.display_name,)
                    msg += "<br/>" + _("Unit Price") + ": %s -> %s <br/>" % (
                    line.price_unit, float(values['price_unit']),)
                msg += "</ul>"
                order.message_post(body=msg)
        return super(PurchaseOrderLine, self).write(values)
