# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models

class ConnectorWarehouseMapping(models.Model):
    _name = "connector.warehouse.mapping"
    _order = 'id desc'
    _description = "Magento Sources"

    name = fields.Many2one(
        'stock.warehouse', string='Warehouse')
    source_code = fields.Char(
        string='Magento Source')
