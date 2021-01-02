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

class InheritResPartner(models.Model):
    _inherit="res.partner"

    @api.depends('delivery_boy_picking_ids', 'delivery_boy_picking_ids.picking_state', 'delivery_boy_picking_ids.commission_amount')
    def _commission_due(self):
        """
        Compute the total pickings delivered commission due amount.
        """
        currency_id = self.env.user.company_id.currency_id
        for partner in self:
            commission_earned = commission_paid = commission_invoiced = 0.0
            for delivery_commision in partner.delivery_boy_picking_ids:
                commission_earned += delivery_commision.commission_amount
                commission_invoiced += delivery_commision.commission_amount if delivery_commision.picking_state == 'invoiced' or delivery_commision.picking_state == 'paid' else 0
                commission_paid += delivery_commision.commission_amount if delivery_commision.picking_state == 'paid' else 0
            partner.update({
                'commission_earned': currency_id.round(commission_earned),
                'commission_invoiced': currency_id.round(commission_invoiced),
                'commission_paid': currency_id.round(commission_paid),
                'amount_due': commission_invoiced - commission_paid,
            })

    is_delivery_boy = fields.Boolean(string="Is a Delivery Boy", copy=False)
    delivery_boy_status = fields.Selection(selection=[('online','Online'),('offline','Offline')], default="offline")
    picking_delivered = fields.Integer(compute='_compute_delivery_boy_pickings_assigned')
    picking_count = fields.Integer(compute='_compute_delivery_boy_pickings_count')

    delivery_boy_picking_ids = fields.One2many(comodel_name="delivery.boy.pickings", inverse_name="partner_id", domain=[('picking_state','in',['invoiced','paid'])])

    commission_earned = fields.Monetary(string='Commission Earned', store=True, readonly=True, compute='_commission_due')
    commission_invoiced = fields.Monetary(string='Commission Invoiced', store=True, readonly=True, compute='_commission_due')
    commission_paid = fields.Monetary(string='Commission Paid', store=True, readonly=True, compute='_commission_due')
    amount_due = fields.Monetary(string='Due Amount', store=True, readonly=True, compute='_commission_due')

    def toggle_is_delivery_boy(self):
        for user in self:
            if self.is_delivery_boy:
                self.is_delivery_boy = False
            else:
                self.is_delivery_boy = True

    def _compute_delivery_boy_pickings_assigned(self):
        for partner in self:
            delivered = self.env['delivery.boy.pickings'].search_count([('partner_id','=',partner.id),('picking_state','in',('delivered','invoiced','paid'))])
            partner.picking_delivered = delivered

    def _compute_delivery_boy_pickings_count(self):
        for partner in self:
            count = self.env['delivery.boy.pickings'].search_count([('partner_id','=',partner.id)])
            partner.picking_count = count

    def name_get(self):
        if self.env.context.get('name_get_override', False):
            res = []
            for record in self:
                res.append((record.id, record.name+" [ Online ]" if record.delivery_boy_status == 'online' else record.name+" [ Offline ]"))
            return res

        return super(InheritResPartner,self).name_get()
