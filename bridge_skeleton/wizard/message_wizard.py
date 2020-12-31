# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models


class MessageWizard(models.TransientModel):
    _name = "message.wizard"
    _description = "Message Wizard"
    
    text = fields.Text(string='Message', readonly=True, translate=True)

    def genrated_message(self, message, name='Message/Summary'):
        partial_id = self.create({'text':message}).id
        return {
            'name':name,
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'message.wizard',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
        }
