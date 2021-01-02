# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import fields,models


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	viewed  = fields.Boolean('Viewed by Sales Person')

	def read(self, *args, **kwargs):
		if len(self) == 1:
			args[0].append('create_uid')
			res = super().read(*args,**kwargs)
			if res[0].get('create_uid') != self._uid:
				self.write({'viewed':True})
		else:
			res = super().read(*args,**kwargs)
		return res
