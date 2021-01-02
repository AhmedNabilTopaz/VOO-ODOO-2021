# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models

class SalespersonWizard(models.TransientModel):
    _name = "salesperson.wizard"
    _description = "Salesperson Wizard"

    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)])

    def selectSalePerson(self):
        partial = self.create({})
        return {
            'name': ("Set Salesperson"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'salesperson.wizard',
            'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': self._context,
            'domain': '[]',
        }

    def setSalesPerson(self):
        orderObjs = self.env['sale.order'].browse(self._context.get('active_ids'))
        orderObjs.write({
            'user_id':self.user_id.id
        })
        return self.env['wk.wizard.message'].genrated_message('Salesperson has been successfully assigned inside the orders')
