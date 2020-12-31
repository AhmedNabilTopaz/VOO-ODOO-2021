# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models
from odoo.exceptions import UserError


Carrier_Code = [
    ('custom', 'Custom Value'),
    ('dhl', 'DHL (Deprecated)'),
    ('fedex', 'Federal Express'),
    ('ups', 'United Parcel Service'),
    ('usps', 'United States Postal Service'),
    ('dhlint', 'DHL')
]


class StockPicking(models.Model):
    _inherit = "stock.picking"

    carrier_code = fields.Selection(
        Carrier_Code,
        string='Ecomm Carrier',
        default="custom",
        help="Ecomm Carrier")
    ecomm_shipment = fields.Char(
        string='Ecomm Shipment',
        help="Contains Ecomm Order Shipment Number (eg. 300000008)")

    def action_done(self):
        self.skeleton_pre_shipment()
        res = super().action_done()
        self.skeleton_post_shipment(res)
        return res

    def skeleton_pre_shipment(self):
        return True

    def skeleton_post_shipment(self, result):
        ctx = dict(self._context or {})
        snippet_obj = self.env['connector.snippet']
        ecomm_cannels = dict(snippet_obj._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            return True
        for picking in self.filtered(lambda obj : obj.picking_type_code == 'outgoing'):
            sale_order = picking.sale_id
            if sale_order.name == picking.origin and sale_order.ecommerce_channel in ecomm_cannels:
                for ecomm in ecomm_cannels:
                    tracking_data = picking.get_tracking_data()
                    if tracking_data:
                        ctx['tracking_data'] = tracking_data
                    response = snippet_obj.with_context(ctx).manual_connector_order_operation('shipment', ecomm, sale_order, picking)
                    picking.ecomm_shipment = response.get('ecomm_shipment', '')


    def ecomm_tracking_sync(self):
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        for picking_obj in self:
            sale_order = picking_obj.sale_id
            track_vals = picking_obj.get_tracking_data()
            if track_vals:
                track_vals['ecom_shipment'] = picking_obj.ecomm_shipment
                for ecomm in ecomm_cannels:
                    if hasattr(self, '%s_sync_tracking_no' % ecomm):
                        getattr(self, '%s_sync_tracking_no' % ecomm)(picking_obj, sale_order, track_vals)
            else:
                raise UserError(
                    'Warning! Sorry No Carrier Tracking No. Found or Please Select Connector Carrier !!!')
    
    def get_tracking_data(self):
        carrier_code = self.carrier_code
        carrier_tracking_no = self.carrier_tracking_ref
        if carrier_tracking_no and carrier_code:
            return {
                'track_number': carrier_tracking_no,
                'carrier_code': carrier_code,
                'title': dict(Carrier_Code)[carrier_code],
            }
