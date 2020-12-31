# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models


class ConnectorSyncHistory(models.Model):
    _name = "connector.sync.history"
    _order = 'id desc'
    _description = "Ecomm Synchronization History"

    status = fields.Selection([
        ('yes', 'Successfull'),
        ('no', 'Un-Successfull')
    ], string='Status')
    action_on = fields.Selection([
        ('product', 'Product'),
        ('category', 'Category'),
        ('customer', 'Customer'),
        ('api', 'API'),
        ('order', 'Order')
    ], string='Action On')
    action = fields.Selection([
        ('a', 'Import'),
        ('b', 'Export'),
        ('c', 'Update')
    ], string='Action')
    instance_id = fields.Many2one(
        'connector.instance', string='Connector Instance')
    ecommerce_channel = fields.Selection(
        related="instance_id.ecomm_type", 
        string="eCommerce Channel", store=True)
    create_date = fields.Datetime(string='Created Date')
    error_message = fields.Text(string='Summary')
