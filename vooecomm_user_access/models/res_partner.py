# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,fields,models


class ResPartner(models.Model):
	_inherit = 'res.partner'

	warehouse_id = fields.Many2one('stock.warehouse','Warehouse')
