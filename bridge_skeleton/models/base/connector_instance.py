# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import re

from odoo import _, api, fields, models
from odoo.addons.base.models.res_partner import _lang_get
from odoo.exceptions import UserError


class ConnectorInstance(models.Model):
    _name = "connector.instance"
    _inherit = ['mail.thread']
    _description = "Connector Instance Configuration"
    _rec_name = 'instance_name'

    def _default_instance_name(self):
        return self.env[
            'ir.sequence'].next_by_code('connector.instance')


    def _default_category(self):
        ctx = dict(self._context or {})
        categId = ctx.get('categ_id', False)
        if categId:
            return categId
        try:
            return self.env['ir.model.data'].get_object_reference(
                'product', 'product_category_all')[1]
        except ValueError:
            return False


    @api.model
    def _get_multi_instances(self):
        ''' Dict of ecomm and thier modules
            e.g {'ecomm_name' : ['multi_instance_module', 'hybrid_module']}
        '''
        return {}


    @api.model
    def _get_ecomm_types(self):
        return self.env['connector.snippet']._get_ecomm_extensions()


    name = fields.Char(
        string='Base URL',
        track_visibility="onchange",
        required=True,
    )
    instance_name = fields.Char(
        string='Instance Name',
        default=lambda self: self._default_instance_name())
    ecomm_type = fields.Selection(
        selection='_get_ecomm_types',
        string="Ecomm",
        required=True)
    user = fields.Char(
        string='API User Name',
        track_visibility="onchange",
        required=True)
    pwd = fields.Char(
        string='API Password',
        track_visibility="onchange",
        required=True)
    status = fields.Char(string='Connection Status', readonly=True)
    active = fields.Boolean(
        string="Active",
        track_visibility="onchange",
        default=True)
    connection_status = fields.Boolean(
        string="Connectivity Status", default=False)
    credential = fields.Boolean(
        string="Show/Hide Credentials Tab",
        default=True,
        help="If Enable, Credentials tab will be displayed, "
        "And after filling the details you can hide the Tab.")
    notify = fields.Boolean(
        string='Notify Customer By Email',
        default=True,
        help="If True, customer will be notify"
        "during order shipment and invoice, else it won't.")
    language = fields.Selection(
        _lang_get, string="Default Language", default=api.model(
            lambda self: self.env.lang), help="Selected language is loaded in the system, "
        "all documents related to this contact will be synched in this language.")
    category = fields.Many2one(
        'product.category',
        string="Default Category",
        default=lambda self: self._default_category(),
        help="Selected Category will be set default category for odoo's product, "
        "in case when Ecomm product doesn\'t belongs to any catgeory.")
    state = fields.Selection([
            ('enable','Enable'),
            ('disable','Disable')
        ],
        string='Status',
        default="enable",
        help="status will be consider during order invoice, "
        "order delivery and order cancel, to stop asynchronous process at other end.",
        size=100)
    inventory_sync = fields.Selection([
            ('enable','Enable'),
            ('disable','Disable')
        ],
        string='Inventory Update',
        default="enable",
        help="If Enable, Invetory will Forcely Update During Product Update Operation.",
        size=100)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        default=lambda self: self.env['sale.order']._default_warehouse_id(),
        help="Used During Inventory Synchronization From Ecommerce to Odoo.")
    location_id = fields.Many2one(
        related='warehouse_id.lot_stock_id', string='Location')
    connector_stock_action = fields.Selection([
        ('qoh', 'Quantity on hand'), 
        ('fq', 'Forecast Quantity')
        ],
        default='qoh',
        string='Stock Management',
        help="Manage Stock")
    connector_discount_product = fields.Many2one(
        'product.product',
        string="Discount Product",
        help="""Service type product used for Discount purposes.""")
    connector_coupon_product = fields.Many2one(
        'product.product',
        string="Coupon Product",
        help="""Service type product used in Coupon.""")
    connector_payment_term = fields.Many2one(
        'account.payment.term',
        string="Ecommerce Payment Term",
        help="""Default Payment Term Used In Sale Order.""")
    connector_sales_team = fields.Many2one(
        'crm.team',
        string="Ecommerce Sales Team",
        help="""Default Sales Team Used In Sale Order.""")
    connector_sales_person = fields.Many2one(
        'res.users',
        string="Ecommerce Sales Person",
        help="""Default Sales Person Used In Sale Order.""")
    connector_sale_order_invoice = fields.Boolean(
        string="Invoice Update",
        help="enable for update invoice status at Ecommerce")
    connector_sale_order_shipment = fields.Boolean(
        string="Shipping Update",
        help="enable for update shipment status at Ecommerce")
    connector_sale_order_cancel = fields.Boolean(
        string="Cancel Update",
        help="enable for update cancel status at Ecommerce")
    create_date = fields.Datetime(string='Created Date')
    correct_mapping = fields.Boolean(string='Correct Mapping', default=True)
    current_instance = fields.Boolean(string = "View Status")

    @api.model
    def create(self, vals):
        if 'name' in vals:
            frontEnd = vals.get('name', '').strip('/')
            vals['name'] = frontEnd
        active_connections = self.search([('active', '=', True)])
        multi_instance_check = self._get_multi_instances().get(vals.get('ecomm_type'))
        is_multi_instance = False
        if self.env['ir.module.module'].sudo().search(
                [('name', 'in', multi_instance_check)], limit=1).state == 'installed':
            is_multi_instance = True
        if vals.get('active') and active_connections and not is_multi_instance:
            raise UserError(
                _('Warning!\nSorry, Only one active connection is allowed.'))
        vals['instance_name'] = self.env[
            'ir.sequence'].next_by_code('connector.instance')
        res = super().create(vals)
        self.env['connector.dashboard']._create_dashboard(res)
        return res

    def write(self, vals):
        if 'name' in vals:
            frontEnd = vals.get('name', '').strip('/')
            vals['name'] = frontEnd
        active_connections = self.search([('active', '=', True)])
        is_multi_instance = False
        multi_instance_check = self._get_multi_instances().get(vals.get('ecomm_type'))
        if self.env['ir.module.module'].sudo().search(
                [('name', 'in', multi_instance_check)], limit=1).state == 'installed':
            is_multi_instance = True
        if vals:
            if len(active_connections) > 0 and vals.get(
                    'active') and not is_multi_instance:
                raise UserError(
                    _('Warning!\nSorry, Only one active connection is allowed.'))
            for instance_obj in self:
                if not instance_obj.instance_name:
                    vals['instance_name'] = self.env[
                        'ir.sequence'].next_by_code('connector.instance')
        return super().write(vals)

    def test_connection(self):
        self.ensure_one()
        if hasattr(self, 'test_%s_connection' % self.ecomm_type):
            return getattr(self, 'test_%s_connection' % self.ecomm_type)()

    @api.model
    def _create_connection(self):
        """ create a connection between Odoo and Ecommerce 
                returns: False or Dict"""
        instance_id = self._context.get('instance_id', False)
        response = {}
        if instance_id:
            instance_obj = self.browse(instance_id)
            if hasattr(self, '_create_%s_connection' % instance_obj.ecomm_type):
                response = getattr(self, '_create_%s_connection' % instance_obj.ecomm_type)()
        return response
