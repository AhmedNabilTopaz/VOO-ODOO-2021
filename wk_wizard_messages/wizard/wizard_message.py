# -*- coding: utf-8 -*-
################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class WkWizardMessage(models.TransientModel):
	_name = "wk.wizard.message"
	_description = "Message Wizard"

	text = fields.Text(string='Message')
	
	def genrated_message(self,message,name='Message/Summary'):
		partial_id = self.create({'text':message}).id
		return {
			'name':name,
			'view_mode': 'form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'wk.wizard.message',
			'res_id': partial_id,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'domain': '[]',
		}