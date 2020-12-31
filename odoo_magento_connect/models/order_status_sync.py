# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

# Attribute Sync Operation

from odoo import api, models

class ConnectorSnippet(models.TransientModel):
    _inherit = "connector.snippet"

    def magento_after_order_cancel(self, connection, increment_id, ecomm_order_id=0):
        return self.magento_order_status_sync_operation(connection, 'cancel', 'OrderCancel', increment_id)

    def magento_after_order_shipment(self, connection, increment_id, ecomm_order_id=0):
        return self.magento_order_status_sync_operation(connection, 'shipment', 'OrderShipment', increment_id)

    def magento_after_order_invoice(self, connection, increment_id, ecomm_order_id=0):
        return self.magento_order_status_sync_operation(connection, 'invoice', 'OrderInvoice', increment_id)

    def magento_order_status_sync_operation(self, connection, opr, api_opr, increment_id):
        text, status, ecomm_shipment = '', 'no', ''
        if connection.get('status', ''):
            order_data = {'orderId': increment_id}
            ctx = dict(self._context or {})
            item_data = ctx.get('itemData')
            if item_data :
                tracking_data = ctx.get('tracking_data')
                if tracking_data :
                    item_data['tracking_data'] = tracking_data
                order_data.update(itemData=item_data)
            api_response = self.with_context(ctx).callMagentoApi(
                baseUrl=connection.get('url', ''),
                url='/V1/odoomagentoconnect/' + api_opr,
                method='post',
                token=connection.get('token', ''),
                data=order_data
            )
            if api_response:
                text = '%s of order %s has been successfully updated on magento.' % (opr, increment_id)
                status = 'yes'
                if api_opr == "OrderShipment":
                    ecomm_shipment = api_response
            else:
                text = 'Magento %s Error For Order %s , Error' % (opr, increment_id)
        else:
            text = 'Magento %s Error For Order %s >> Could not able to connect Magento.' % (opr, increment_id)
        return {
            'text':text,
            'status': status,
            'ecomm_shipment':ecomm_shipment
        }

