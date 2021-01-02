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

from odoo import models,fields,exceptions, _

class InheritStockPicking(models.Model):
    _inherit="stock.picking"

    delivery_boy_partner_id = fields.Many2one(string="Delivery Boy", comodel_name="res.partner", context="{'invisible':False,}", readonly=True, copy=False)
    delivery_boy_picking_id = fields.Many2one(string="Delivery Boy Picking", comodel_name="delivery.boy.pickings", readonly=True, copy=False)

    def action_assign_delivery_boy(self):

        conflict_products = list(filter(lambda move: move.product_uom_qty != move.reserved_availability, self.move_ids_without_package))
        if conflict_products:
            raise exceptions.UserError(_("Cannot assign Delivery Boy\nLess products are processed than the initial demand"))

        if self.delivery_boy_picking_id and self.delivery_boy_picking_id.picking_state != 'assigned':
            raise exceptions.UserError(_("Cannot reassign Delivery Boy\nAs the respective picking with Delivery boy Picking Reference Id %s has been already delivered")%(self.delivery_boy_picking_id.name))

        wizard_id = self.env['wizard.select.delivery.boy'].create({
        'stock_picking_id': self.id,
        })
        ctx = self.env.context.copy()
        ctx['delivery_boy_partner_id'] =  self.delivery_boy_partner_id.id
        return {
            'name':'Select Delivery Boy',
            'view_mode': 'form',
            'view_id': self.env.ref('delivery_boy.view_select_delivery_boy_wizard').id,
            'res_model': 'wizard.select.delivery.boy',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard_id.id,
            'context': ctx,
            }
