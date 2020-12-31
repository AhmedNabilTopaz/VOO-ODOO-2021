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
    _name = "wk.skeleton"
    _description = " Skeleton for all XML RPC imports in Odoo"


    @api.model
    def get_ecomm_href(self, getcommtype=False):
        href_list = {}
        if getcommtype=='magento':
            href_list = {
            'user_guide':'https://webkul.com/blog/magento-openerp-bridge/',
            'rate_review':'https://store.webkul.com/Magento-OpenERP-Bridge.html#tabreviews',
            'extension':'https://store.webkul.com/Magento-Extensions/ERP.html',
            'name' : 'MAGENTO',
            'short_form' : 'Mob',
            'img_link' : '/bridge_skeleton/static/src/img/magento-logo.png'
            }
        if getcommtype=='test2':
            href_list = {
            'user_guide':'https://store.webkul.com/Prestashop-Openerp-Connector.html',
            'rate_review':'https://store.webkul.com/Prestashop-Openerp-Connector.html#tabreviews',
            'extension':'https://store.webkul.com/PrestaShop-Extensions.html',
            'name' : 'PRESTASHOP',
            'short_form' : 'Pob',
            'img_link' : '/bridge_skeleton/static/src/img/pob-logo.png'
            }
        return href_list



    @api.model
    def set_extra_values(self):
        """ Add extra values"""
        return True
    # Order Status Updates

    @api.model
    def set_order_cancel(self, order_id):
        """Cancel the order in Odoo via requests from XML-RPC
                @param order_id: Odoo Order ID
                @param context: Mandatory Dictionary with key 'ecommerce' to identify the request from E-Commerce
                @return: A dictionary of status and status message of transaction"""
        ctx = dict(self._context or {})
        status = True
        status_message = "Order Successfully Cancelled."
        isVoucherInstalled = False
        try:
            saleObj = self.env['sale.order'].browse(order_id)
            status_message = "Odoo Order %s Cancelled Successfully." % (
                saleObj.name)
            if self.env['ir.module.module'].sudo().search(
                    [('name', '=', 'account_voucher')], limit=1).state == 'installed':
                isVoucherInstalled = True
                voucherModel = self.env['account.voucher']
            if saleObj.invoice_ids:
                for invoiceObj in saleObj.invoice_ids:
                    invoiceObj.journal_id.update_posted = True
                    if invoiceObj.state == "paid" and isVoucherInstalled:
                        for paymentObj in invoiceObj.payment_ids:
                            voucherObjs = voucherModel.search(
                                [('move_ids.name', '=', paymentObj.name)])
                            if voucherObjs:
                                for voucherObj in voucherObjs:
                                    voucherObj.journal_id.update_posted = True
                                    voucherObj.cancel_voucher()
                    invoiceObj.action_cancel()
            if saleObj.picking_ids:
                if 'done' in saleObj.picking_ids.mapped('state'):
                    donePickingNames = saleObj.picking_ids.filtered(
                        lambda pickingObj: pickingObj.state == 'done').mapped('name')
                    status = True
                    status_message = "Odoo Order %s Cancelled but transferred pickings can't cancelled," % (
                        saleObj.name) + " Please create return for pickings %s !!!" % (", ".join(donePickingNames))
            saleObj.with_context(ctx).action_cancel()
        except Exception as e:
            status = False
            status_message = "Odoo Order %s Not cancelled. Reason: %s" % (
                saleObj.name, str(e))
        finally:
            return {
                'status_message': status_message,
                'status': status
            }

    @api.model
    def get_default_configuration_data(self, ecommerce_channel, instance_id):
        """@return: Return a dictionary of Sale Order keys by browsing the Configuration of Bridge Module Installed"""
        connection_obj = self.env['connector.instance'].browse(instance_id)
        sale_data = {
            'payment_term_id': connection_obj.connector_payment_term and connection_obj.connector_payment_term.id,
            'team_id': connection_obj.connector_sales_team and connection_obj.connector_sales_team.id,
            'user_id': connection_obj.connector_sales_person and connection_obj.connector_sales_person.id,
        }
        if hasattr(self, 'get_%s_configuration_data' % ecommerce_channel):
            response = getattr(
                self, 'get_%s_configuration_data' %
                ecommerce_channel)(connection_obj)
            sale_data.update(response)
        return sale_data

    @api.model
    def create_order_mapping(self, mapData):
        """Create Mapping on Odoo end for newly created order
        @param order_id: Odoo Order ID
        @context : A dictionary consisting of e-commerce Order ID"""

        self.env['connector.order.mapping'].create(mapData)
        return True

    @api.model
    def create_order(self, sale_data):
        """ Create Order on Odoo along with creating Mapping
        @param sale_data: dictionary of Odoo sale.order model fields
        @param context: Standard dictionary with 'ecommerce' key to identify the origin of request and
                                        e-commerce order ID.
        @return: A dictionary with status, order_id, and status_message"""
        ctx = dict(self._context or {})
        # check sale_data for min no of keys presen or not
        order_name, order_id, status, status_message = "", False, True, "Order Successfully Created."
        ecommerce_channel = sale_data.get('ecommerce_channel')
        instance_id = ctx.get('instance_id', 0)
        ecommerce_order_id = sale_data.pop('ecommerce_order_id', 0)
        config_data = self.get_default_configuration_data(ecommerce_channel, instance_id)
        sale_data.update(config_data)

        try:
            order_obj = self.env['sale.order'].create(sale_data)
            order_id = order_obj.id
            order_name = order_obj.name
            mapping_data = {
                'ecommerce_channel': ecommerce_channel,
                'odoo_order_id': order_id,
                'ecommerce_order_id': ecommerce_order_id,
                'instance_id': instance_id,
                'name': sale_data['origin'],
            }
            self.create_order_mapping(mapping_data)
        except Exception as e:
            status_message = "Error in creating order on Odoo: %s" % str(e)
            status = False
        finally:
            return {
                'order_id': order_id,
                'order_name': order_name,
                'status_message': status_message,
                'status': status
            }

    @api.model
    def confirm_odoo_order(self, order_id):
        """ Confirms Odoo Order from E-Commerce
        @param order_id: Odoo/ERP Sale Order ID
        @return: a dictionary of True or False based on Transaction Result with status_message"""
        #REMOVED this long as python3 not supported long  # if isinstance(order_id, (int, long)):
        if isinstance(order_id, (int)):
            order_id = [order_id]
        ctx = dict(self._context or {})
        status = True
        status_message = "Order Successfully Confirmed!!!"
        try:
            saleObj = self.env['sale.order'].browse(order_id)
            saleObj.action_confirm()
        except Exception as e:
            status_message = "Error in Confirming Order on Odoo: %s" % str(e)
            status = False
        finally:
            return {
                'status': status,
                'status_message': status_message
            }
