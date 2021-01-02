# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import fields,models


class Warehouse(models.Model):
	_inherit = 'stock.warehouse'

	def _user_id_domain(self):
		return [
			('groups_id','in',(self.env.ref('vooecomm_user_access.group_pnp_plus').ids)),
			('groups_id','not in',self.env.ref('vooecomm_user_access.group_pnp_not').ids),
		]

	user_id = fields.Many2one(
		comodel_name='res.users',
		string='Sales Person',
		domain=_user_id_domain,
	)

	delivery_boys = fields.One2many(
		comodel_name='res.partner',
		inverse_name='warehouse_id',
		string='Delivery Boys',
		domain=[('is_delivery_boy','=',True)],
	)

