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

    def create_magento_product_attribute(self, name, odoo_id, connection, ecomm_attribute_code):
        status, ecomm_id, error = connection.get('status', False), 0, ''
        if status:
            url = connection.get('url', '')
            token = connection.get('token', '')
            attrribute_data = {"attribute": {
                'attributeCode': ecomm_attribute_code,
                'scope': 'global',
                'frontendInput': 'select',
                'isRequired': 0,
                'frontendLabels': [{'storeId': 0, 'label': name}]
               }
            }
            attribute_response = self.callMagentoApi(
                baseUrl=url,
                url='/V1/products/attributes',
                method='post',
                token=token,
                data=attrribute_data
            )
            ecomm_id = 0
            if attribute_response and attribute_response.get('attribute_id', 0) > 0:
                ecomm_id, status = attribute_response['attribute_id'], 1
            else:
                attribute_response = self.callMagentoApi(
                    baseUrl=url,
                    url='/V1/products/attributes/' + ecomm_attribute_code,
                    method='get',
                    token=token,
                )
                if attribute_response and attribute_response.get('attribute_id') > 0:
                    ecomm_id, status = attribute_response.get('attribute_id'), 1
                else:
                    status, error = 0, 'Attribute Not found at magento.'
        return {'status': status, 'ecomm_id':ecomm_id, 'error':error}

    def create_magento_product_attribute_value(self, ecomm_id, attribute_obj, ecomm_attribute_code, instance_id, connection):
        if connection.get('status', False) and ecomm_attribute_code:
            attribute_value_data, token, url = {}, connection.get('token', ''), connection.get('url', '')
            for value_obj in attribute_obj.value_ids:
                value_name = value_obj.name
                value_id = value_obj.id
                attribute_value_data[value_name] = value_id
                if not self.env['connector.option.mapping'].search([('odoo_id', '=', value_id), ('instance_id', '=', instance_id)], limit=1):
                    position = value_obj.sequence
                    self.create_magento_attribute_value(url, token, ecomm_attribute_code, value_id, value_name, position)
            self.map_magento_attribute_values(url, token, ecomm_attribute_code, attribute_value_data)
        return True

    @api.model
    def create_magento_attribute_value(self, url, token, ecomm_attribute_code, value_id, name, position='0'):
        if token:
            name = name.strip()
            options_data = {"option": {
                "label": name,
                "sortOrder": position,
                "isDefault": 0,
                'storeLabels': [{'storeId': 0, 'label': name}]
            }}
            return self.callMagentoApi(
                baseUrl=url,
                url='/V1/products/attributes/' + ecomm_attribute_code + '/options',
                method='post',
                token=token,
                data=options_data
            )
        return True

    @api.model
    def map_magento_attribute_values(self, url, token, ecomm_attribute_code, attribute_value_data):
        option_response = self.callMagentoApi(
            baseUrl=url,
            url='/V1/products/attributes/' + ecomm_attribute_code + '/options',
            method='get',
            token=token
        )
        if type(option_response) is list:
            instance_id = self._context.get('instance_id')
            map_value_model = self.env['connector.option.mapping']
            for mage_option in option_response:
                if mage_option.get('value'):
                    ecomm_id = int(mage_option.get('value', 0))
                    mage_label = mage_option['label']
                    map_value_obj = map_value_model.search([
                        ('ecomm_id', '=', ecomm_id), 
                        ('instance_id', '=', instance_id)
                    ], limit=1)
                    if not map_value_obj and attribute_value_data.get(mage_label):
                        odoo_id = attribute_value_data[mage_label]
                        self.create_odoo_connector_mapping('connector.option.mapping', int(ecomm_id), odoo_id, instance_id)
                        map_data = {'option': {
                            'name': mage_label, 
                            'magento_id': ecomm_id, 
                            'odoo_id': odoo_id, 
                            'created_by': 'Odoo'
                        }}
                        self.callMagentoApi(
                            baseUrl=url,
                            url='/V1/odoomagentoconnect/option',
                            method='post',
                            token=token,
                            data=map_data
                        )
        return True