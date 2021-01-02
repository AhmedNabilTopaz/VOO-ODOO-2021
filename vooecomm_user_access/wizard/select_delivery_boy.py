# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,fields,models

class SelectDeliveryBoy(models.TransientModel):
	_inherit = 'wizard.select.delivery.boy'

	@api.depends('stock_picking_id')
	def _compute_partner_ids(self):
		for rec in self:
			rec.partner_ids = self.stock_picking_id.sale_id.warehouse_id.delivery_boys

	partner_ids = fields.Many2many('res.partner',compute=_compute_partner_ids)
