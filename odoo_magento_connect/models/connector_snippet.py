# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import json
import re

import requests
from odoo import api, models
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class ConnectorSnippet(models.TransientModel):
    _inherit = "connector.snippet"

    @api.model
    def _get_ecomm_extensions(self):
        res = super(ConnectorSnippet, self)._get_ecomm_extensions().__add__([('magento', 'Magento')])
        return res

    @api.model
    def callMagentoApi(self, url, method, token='', data={}, params=[], base_url='', **kwargs):
        _logger.debug("Call %r : %r ",method.upper(),url)
        action = 'a'
        connection_model = self.env['connector.instance']
        if not token :
            connection = connection_model._create_connection()
            if connection:
                base_url = connection.get('url')
                token = connection.get('token')
        instance_id = self._context.get('instance_id')
        if not base_url:
            if instance_id:
                connection_obj = connection_model.browse(instance_id)
            else :
                connection_obj = connection_model.search([('active', '=', True)], limit=1)
            base_url = connection_obj.name

        api_url = base_url + "/index.php/rest" + url
        token = token.replace('"', "")
        user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
        headers = {'Authorization': token,
                    'Content-Type': 'application/json', 'User-Agent': user_agent}

        if data:
            tmp = json.dumps(data,indent=4)
            _logger.debug("Request Data: "+tmp)

        if method == 'get' :
            response = requests.get(
                api_url, headers=headers, verify=False, params=params)
        elif method == 'post' :
            action = 'b'
            payload = json.dumps(data)
            response = requests.post(
                api_url, headers=headers, data=payload, verify=False, params=params)
        elif method == 'put' :
            action = 'c'
            payload = json.dumps(data)
            response = requests.put(
                api_url, headers=headers, data=payload, verify=False, params=params)
        elif method == 'delete' :
            response = requests.delete(
                api_url, headers=headers, verify=False, params=params)
        else :
            return "Wrong API method is selected."
        try:
            response_data = json.loads(response.text)
        except Exception as e:
            response_data = {
                'message': str(e),
                'parameters': {'reason': response.reason, 'text': response.text}
            }
        tmp = json.dumps(response_data, indent=4)
        _logger.debug("Response: "+tmp)
        if not response.ok:
            self.env['connector.sync.history'].create({
                'status': 'no',
                'instance_id': instance_id,
                'action_on': 'api',
                'action': action,
                'error_message': "Error in calling api "+ url +" :\n"+response_data.get('message', '') +
                    "\n"+str(response_data.get('parameters', ''))
            })
            return {}
        return response_data

    @api.model
    def sync_attribute_set(self, data):
        ctx = dict(self._context or {})
        res = False
        attr_set_env = self.env['magento.attribute.set']
        set_name = data.get('name')
        set_id = data.get('set_id', 0)
        if set_name and set_id:
            instance_id = ctx.get('instance_id', False)
            set_map_obj = attr_set_env.search([
                    ('set_id', '=', set_id),
                    ('instance_id', '=', instance_id)
                ], limit=1)
            if not set_map_obj:
                set_map_obj = attr_set_env.create({
                    'name': set_name,
                    'set_id': set_id,
                    'created_by': 'Magento',
                    'instance_id': instance_id
                })
            if set_map_obj:
                update_dict = {
                    'name': set_name
                }
                attribute_ids = data.get('attribute_ids', [])
                if attribute_ids:
                    update_dict['attribute_ids'] = [
                        (6, 0, attribute_ids)]
                else:
                    update_dict['attribute_ids'] = [[5]]
                res = set_map_obj.write(update_dict)
        return res

    def create_magento_connector_mapping(self, model, data, connection):
        if connection.get('status', False):
            ecomm_id, odoo_id, name = data.get('ecomm_id', 0), data.get('odoo_id', 0), data.get('name', 0)
            if model == 'connector.attribute.mapping':
                data = {'attribute': {
                            'name': name,
                            'magento_id': ecomm_id,
                            'odoo_id': odoo_id,
                            'created_by': 'Odoo'
                        }}
                self.callMagentoApi(
                        baseUrl=connection.get('url'),
                        url='/V1/odoomagentoconnect/attribute',
                        method='post',
                        token=connection.get('token'),
                        data=data
                    )
            elif model == 'connector.category.mapping':
                data = {'category': {
                            'magento_id': ecomm_id,
                            'odoo_id': odoo_id,
                            'created_by': 'Odoo'
                        }}
                self.callMagentoApi(
                        baseUrl=connection.get('url'),
                        url='/V1/odoomagentoconnect/category',
                        method='post',
                        token=connection.get('token'),
                        data=data
                    )
        return True

    def update_magento_connector_mapping(self, model, data, connection):
        if connection.get('status', False):
            ecomm_id, odoo_id, name = data.get('ecomm_id', 0), data.get('odoo_id', 0), data.get('name', 0)
            if model == 'connector.category.mapping':
                self.callMagentoApi(
                    baseUrl=connection.get('url'),
                    url='/V1/odoomagentoconnect/category',
                    method='put',
                    token=connection.get('token'),
                    data={'categoryId': ecomm_id,'name': name}
                )
        return True

    def manual_connector_order_operation(self, opr, ecomm, sale_order, opr_obj=False):
        if opr == 'shipment':
            itemData = {}
            for moveLine in opr_obj.move_line_ids:
                productSku = moveLine.product_id.default_code or False
                if productSku :
                    quantity = moveLine.qty_done
                    itemData[productSku] = int(quantity)
            self = self.with_context(itemData=itemData)
        return super(ConnectorSnippet, self).manual_connector_order_operation(
            opr, ecomm, sale_order, opr_obj
        )

    def create_magento_connector_odoo_mapping(self, mapping_data, model):
        magento_stock_id = self._context.get('magento_stock_id', False)
        if model == 'connector.product.mapping' and magento_stock_id:
            mapping_data.update(magento_stock_id=magento_stock_id)
        return mapping_data

