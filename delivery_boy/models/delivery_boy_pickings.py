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

from odoo import models,fields,api,exceptions, _

class DeliveryBoyPickings(models.Model):
    _name="delivery.boy.pickings"
    _description = "Delivery Boy Pickings"

    name = fields.Char('Reference', default='/', index=True, copy=False)
    assigned_date = fields.Datetime('Assigned Date')
    sale_order_id = fields.Many2one(comodel_name="sale.order", compute="_set_order")
    picking_id = fields.Many2one(comodel_name="stock.picking", domain="[('sale_id', '!=', False)]")
    delivery_token = fields.Char('Delivery Token', readonly=True)
    picking_state = fields.Selection(
        selection=[('assigned','Assigned'),('accept','Accept'),('denied','Denied'),('delivered','Delivered'),('cancel','Canceled'),('invoiced','Invoiced'),('paid','Paid')],
        default="assigned",
        copy=False,
        )
    partner_id = fields.Many2one(string="Delivery Boy", comodel_name="res.partner", context="{'invisible':False,}", domain="[('is_delivery_boy','=',True)]")

    commission_date = fields.Date(copy=False)
    commission_amount = fields.Float(string="Commission Amount")
    commission_type = fields.Selection(selection=[('ppo','Pay Per Order'),('ppp','Pay Per Product')])
    matrix_type = fields.Selection(selection=[('fix','Fixed'),('percent','Percentage')])
    program_commission_amount = fields.Float(string="Prog. Commission")
    currency_id = fields.Many2one(
                    'res.currency',
                    'Currency',
                    default=lambda self: self.env.user.company_id.currency_id.id
                    )
    invoice_id = fields.Many2one(comodel_name="account.move", domain="[('delivery_boy_invoice','=', True)]")
    msg = fields.Text()

    def _calc_commission_amount(self, db_program_id):
        commission_amt = 0.0
        if db_program_id.commission_type == 'ppo':
            if db_program_id.matrix_type == 'fix':
                commission_amt = db_program_id.commission_amount
            else:
                order_value = self.picking_id.sale_id.amount_total
                commission_amt = float(order_value * db_program_id.commission_amount) / 100
        elif db_program_id.commission_type == 'ppp':
            if db_program_id.matrix_type == 'fix':
                products_count = 0
                for product in self.picking_id.sale_id.order_line:
                    products_count += product.product_uom_qty
                commission_amt = products_count * db_program_id.commission_amount
            else:
                for product in self.picking_id.sale_id.order_line:
                    commission_amt += float(product.price_subtotal * db_program_id.commission_amount) / 100
        return commission_amt

    def write(self, vals):
        delivery_boy_config = self.env['res.config.settings'].sudo().get_db_configuration()
        for db_picking in self:
            if vals.get('picking_state') == 'denied' or vals.get('picking_state') == 'cancel':
                db_picking.picking_id.delivery_boy_partner_id = False
                db_picking.picking_id.delivery_boy_picking_id = False
            elif vals.get('picking_state') == 'accept':
                if delivery_boy_config.get('verify_token'):
                    delivery_boy_config.get('delivery_token_mail_temp_id').send_mail(self.id, force_send=True)
            elif vals.get('picking_state') == 'paid':
                db_picking._pushNotification('p_paid',db_picking.partner_id.id)

        return super(DeliveryBoyPickings,self).write(vals)

    @api.depends('picking_id')
    def _set_order(self):
        for delivery_boy_picking in self:
            if delivery_boy_picking.picking_id.sale_id:
                delivery_boy_picking.sale_order_id = delivery_boy_picking.picking_id.sale_id.id
            else:
                delivery_boy_picking.sale_order_id = False

    def token(self, n):
        import random
        return ''.join([random.choice('aGHIJKLMNObcd12345efABCDEFghij67890kUVWlmnPQRSTopqrstuvwxXYZyz') for i in range(n)])

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('delivery.boy.pickings')
        vals['delivery_token'] = self.token(5)
        return super(DeliveryBoyPickings,self).create(vals)

    def action_delivered(self):
        self.picking_state = 'delivered'
        delivery_boy_config = self.env['res.config.settings'].sudo().get_db_configuration()
        if delivery_boy_config['allow_db_program']:
            self.commission_date = fields.Date.today()
            self.commission_amount = self._calc_commission_amount(delivery_boy_config['program'])
            self.commission_type = delivery_boy_config['program'].commission_type
            self.matrix_type = delivery_boy_config['program'].matrix_type
            self.program_commission_amount = delivery_boy_config['program'].commission_amount
        if delivery_boy_config['auto_validate']:
            total_product_uom_qty = 0.0
            total_reserved_availability = 0.0
            for move_id in self.picking_id.move_ids_without_package:
                if not move_id.quantity_done:
                    move_id.quantity_done = move_id.reserved_availability
                total_product_uom_qty += move_id.product_uom_qty
                total_reserved_availability += move_id.reserved_availability

            if total_reserved_availability < total_product_uom_qty:
                self.msg = _("Please validate the stock picking manually for this delivery boy picking as the products processed are less than the initial demand.")
            else:
                self.picking_id.button_validate()
        if delivery_boy_config['auto_invoice']:
            self.action_create_invoice()

    def action_cancel(self):
        self.picking_state = 'cancel'
        msg = _("Delivery boy Picking with Reference Id %s, has been canceled.")%(self.name)
        partial_id = self.env['msg.wizard'].create({'text': msg})
        self._pushNotification('p_canceled',self.partner_id.id)
        return {
        'name': "Message",
        'view_mode': 'form',
        'view_id': False,
        'res_model': 'msg.wizard',
        'res_id': partial_id.id,
        'type': 'ir.actions.act_window',
        'nodestroy': True,
        'target': 'new',
        }


    def _get_invoice_description(self):
        matrix_type = commission_type = char = None
        if self.matrix_type == 'fix':
            matrix_type = 'Fixed Commission'
            char = self.currency_id.name
        else:
            matrix_type = 'Percent Commission'
            char = '%'

        if self.commission_type == 'ppo':
            commission_type =  'Pay Per Order'
        else:
            commission_type = 'Pay Per Product'

        return _("[ %s ( %s %s) ] %s")%(matrix_type, self.program_commission_amount, char, commission_type)

    def action_create_invoice(self):
        if not self.invoice_id:
            self._create_invoice()
        else:
            raise exceptions.UserError(_("Invoice is already generated for this picking."))

    def _create_invoice(self):
        vals={}
        if len(self) > 1:


            vals={
            'name':_("Total Commission earned"),
            'quantity':1,
            'price_unit':total_commission_amt,

            }

        else:
            vals={
            'name':self._get_invoice_description(),
            'quantity':1,
            'price_unit':self.commission_amount,
            }
            self.picking_state = 'invoiced'
            self._pushNotification('p_invoiced',self.partner_id.id)

        invoice_dict = [
                            { 'invoice_line_ids': [(0, 0, vals)],
                              'type': 'out_invoice',
                              'partner_id':self[0].partner_id.id,
                              'delivery_boy_invoice': True,
                              'invoice_date':fields.Datetime.now().date()
                            }
                        ]
        invoice = self.env['account.move'].with_context(default_type='out_invoice').create(invoice_dict)
        total_commission_amt = 0.0
        for delivery_boy_picking in self:
            delivery_boy_picking.invoice_id = invoice.id
            total_commission_amt += delivery_boy_picking.commission_amount
            delivery_boy_picking.picking_state = 'invoiced'
            delivery_boy_picking._pushNotification('p_invoiced',delivery_boy_picking.partner_id.id)


    @api.model
    def server_action_create_invoice(self):
        """
        Server Action
        Create invoice for a particular delivery boy delivered pickings.
        """
        delivery_boy = self[0].partner_id
        for delivery_boy_picking in self:
            if delivery_boy_picking.picking_state != 'delivered' or delivery_boy_picking.partner_id != delivery_boy:
                raise exceptions.UserError(_("You can only create an invoice for a particular delivery boy delivered pickings"))

        self._create_invoice()

    @api.model
    def demo_set_picking_id(self):
        delivery_boy_pickings = self.sudo().search([])
        stock_pickings =self.env['stock.picking'].sudo().search([('state','=','assigned')])
        for i,delivery_boy_picking in enumerate(delivery_boy_pickings):
            try:
                delivery_boy_picking.picking_id = stock_pickings[i].id
                stock_pickings[i].delivery_boy_partner_id = delivery_boy_picking.partner_id.id
                stock_pickings[i].delivery_boy_picking_id = delivery_boy_picking.id
            except IndexError:
                delivery_boy_picking.picking_id = False

    def _pushNotification(self, condition, partner_id=False):
        try:
            self.ensure_one()
            devices_reg = self.env['delivery.boy.fcm.registered.devices'].sudo().search([('partner_id','=',partner_id),('token','!=',False)])
            for device_reg in devices_reg:
                token = device_reg.token
                notifications = self.env['delivery.boy.push.notification.template'].sudo().search([('condition','=',condition)])
                for n in notifications:
                    n._send({'to':token}, partner_id, self)
        except ValueError as ve:
            _logger.info("---------_pushNotification Exception---------------%r----", ve)
        return True

    def act_delivery_boy_pickings_2_account_invoice(self):
        return {
        'view_mode': 'form',
        # 'view_type': 'form',
        'res_model': 'account.move',
        'res_id': self.invoice_id.id,
        'type': 'ir.actions.act_window',
        'nodestroy': True,
        'target': 'current',
        }
