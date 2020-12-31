# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models


class ConnectorPartnerMapping(models.Model):
    _name = "connector.partner.mapping"
    _inherit = ['connector.common.mapping']
    _order = 'id desc'
    _description = "Ecomm Customers"


    name = fields.Many2one('res.partner', string='Customer Name')
    ecomm_address_id = fields.Char(string='Ecomm Address Id', size=50)
