# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


def _unescape(text):
    ##
    # Replaces all encoded characters by urlib with plain utf8 string.
    #
    # @param text source text.
    # @return The plain text.
    from urllib.parse import unquote_plus
    try:
        text = unquote_plus(text)
        return text
    except Exception as e:
        return text


class WkSkeleton(models.TransientModel):
    _inherit = "wk.skeleton"

    @api.model
    def create_order_shipping_and_voucher_line(self, order_line):
        """ @params order_line: A dictionary of sale ordre line fields
                @params context: a standard odoo Dictionary with context having keyword to check origin of fumction call and identify type of line for shipping and vaoucher
                @return : A dictionary with updated values of order line"""
        ctx = dict(self._context or {})
        instance_id = ctx.get('instance_id', False)
        order_line['product_id'] = self.get_default_virtual_product_id(order_line, instance_id)
        if order_line.get('name', '').startswith('S'):
            order_line['is_delivery'] = True
        order_line.pop('ecommerce_channel', None)
        res = self.create_sale_order_line(order_line)
        return res

    @api.model
    def get_default_virtual_product_id(self, order_line, instance_id):
        odoo_product_id = False
        virtual_name = order_line.get('name')[:1]
        if virtual_name == 'S':
            carrier_obj = self.env['sale.order'].browse(
                order_line.get('order_id')).carrier_id
            odoo_product_id = carrier_obj.product_id.id
        elif virtual_name == 'D':
            connection_obj = self.env['connector.instance'].browse(instance_id)
            odoo_product_obj = connection_obj.connector_discount_product
            if odoo_product_obj:
                odoo_product_id = odoo_product_obj.id
            else:
                odoo_product_id = self.env['product.product'].create({
                    'sale_ok' : False,
                    'name' : order_line.get('name', 'Discount'),
                    'type' : 'service',
                    'list_price' : 0.0,
                    'description': 'Service Type product used by Magento Odoo Bridge for Discount Purposes'
                }).id
                connection_obj.connector_discount_product = odoo_product_id
        else:
            connection_obj = self.env['connector.instance'].browse(instance_id)
            odoo_product_obj = connection_obj.connector_coupon_product
            if odoo_product_obj:
                odoo_product_id = odoo_product_obj.id
            else:
                odoo_product_id = self.env['product.product'].create({
                    'sale_ok' : False,
                    'name' : order_line.get('name', 'Voucher'),
                    'type' : 'service',
                    'list_price' : 0.0,
                    'description': 'Service Type product used by Magento Odoo Bridge for Gift Voucher Purposes'
                }).id
                connection_obj.connector_coupon_product = odoo_product_id
        return odoo_product_id

    @api.model
    def create_sale_order_line(self, order_line_data):
        """Create Sale Order Lines from XML-RPC
        @param order_line_data: A List of dictionary of Sale Order line fields in which required field(s) are 'order_id', `product_uom_qty`, `price_unit`
                `product_id`: mandatory for non shipping/voucher order lines
        @return: A dictionary of Status, Order Line ID, Status Message  """
        status = True
        order_line_id = False
        statusMessage = "Order Line Successfully Created."
        try:
            # To FIX:
            # Cannot call Onchange in sale order line
            productObj = self.env['product.product'].browse(
                order_line_data['product_id'])
            order_line_data.update({'product_uom': productObj.uom_id.id})
            name = order_line_data.get('name', None)
            description = order_line_data.pop('description', None)
            if description :
                order_line_data.update(name=_unescape(description))
            elif name:
                order_line_data.update(name=_unescape(name))
            else:
                order_line_data.update(
                    name=productObj.description_sale or productObj.name
                )
            taxes = order_line_data.get('tax_id', [])
            order_line_data['tax_id'] = [(6, 0, taxes)] if taxes else False
            order_line_id = self.env['sale.order.line'].create(order_line_data)
        except Exception as e:
            statusMessage = "Error in creating order Line on Odoo: %s" % str(e)
            status = False
        finally:
            returnDict = dict(
                order_line_id=0,
                status=status,
                status_message=statusMessage,
            )
            if order_line_id:
                returnDict.update(
                    order_line_id=order_line_id.id
                )
            return returnDict
