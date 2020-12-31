# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


class WkSkeleton(models.TransientModel):
    _inherit = "wk.skeleton"

    @api.model
    def set_order_shipped(self, orderId):
        """Ship the order in Odoo via requests from XML-RPC
        @param order_id: Odoo Order ID
        @param context: Mandatory Dictionary with key 'ecommerce' to identify the request from E-Commerce
        @return:  A dictionary of status and status message of transaction"""
        ctx = dict(self._context or {})
        status = True
        status_message = "Order Successfully Shipped."
        try:
            saleObj = self.env['sale.order'].browse(orderId)
            backOrderModel = self.env['stock.backorder.confirmation']
            if saleObj.state == 'draft':
                self.confirm_odoo_order([orderId])
            if saleObj.picking_ids:
                for pickingObj in saleObj.picking_ids.filtered(
                        lambda pickingObj: pickingObj.picking_type_code == 'outgoing' and pickingObj.state != 'done'):
                    backorder = False
                    ctx['active_id'] = pickingObj.id
                    ctx['picking_id'] = pickingObj.id
                    pickingObj.action_assign()
                    for packObj in pickingObj.move_ids_without_package:
                        if packObj.quantity_done and packObj.quantity_done < packObj.product_uom_qty:
                            backorder = True
                            continue
                        elif packObj.product_uom_qty > 0:
                            packObj.write({'quantity_done': packObj.product_uom_qty})
                        else:
                            packObj.unlink()
                    if backorder:
                        backorderObj = backOrderModel.create(
                            {'pick_ids': [(4, pickingObj.id)]})
                        backorderObj.process()
                    else:
                        pickingObj.button_validate()
                    self.with_context(ctx).set_extra_values()
        except Exception as e:
            status = False
            status_message = "Error in Delivering Order: %s" % str(e)
        finally:
            return {
                'status_message': status_message,
                'status': status
            }

    @api.model
    def set_extra_values(self):
        """ Add extra values"""
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            pickingData = {}
            if 'picking_id' in ctx and 'carrier_tracking_ref' in ctx \
                    and 'carrier_code' in ctx and 'ship_number' in ctx:
                pickingData = {
                    'carrier_tracking_ref' : ctx.get('carrier_tracking_ref',  False),
                    'carrier_code' : ctx.get('carrier_code', 'custom'),
                    'ecomm_shipment' : ctx.get('ship_number', False)
                }
            elif 'ship_number' in ctx:
                pickingData = {
                    'ecomm_shipment' : ctx.get('ship_number')
                }

            if pickingData:
                pickingObj = self.env['stock.picking'].browse(
                    ctx.get('picking_id'))
                pickingObj.write(pickingData)
        return True