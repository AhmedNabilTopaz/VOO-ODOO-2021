# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import logging
_logger = logging.getLogger(__name__)

from odoo import models,fields,api, _

class InheritAccountInvoice(models.Model):
    _inherit="account.move"

    delivery_boy_invoice = fields.Boolean()
    delivery_boy_picking_ids = fields.One2many(
    string="Reports",
    comodel_name="delivery.boy.pickings",
    inverse_name="invoice_id")


    def write(self, vals):
        to_pay_invoices =self.filtered(lambda inv: inv.state != 'paid' and inv.delivery_boy_invoice)
        for to_pay_invoice in to_pay_invoices:
            for picking in to_pay_invoice.delivery_boy_picking_ids:
                picking.picking_state = 'paid'
        return super(InheritAccountInvoice, self).write(vals)
