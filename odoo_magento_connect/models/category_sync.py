# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


class ConnectorSnippet(models.TransientModel):
    _inherit = "connector.snippet"

    def create_magento_category(self, odoo_id, parent_categ_id, name, connection):
        status, ecomm_id, error = connection.get('status', False), 0, ''
        if status and odoo_id > 0:
            category_data = {"category": {
                'name': name,
                'parentId': parent_categ_id,
                'isActive': 1,
                'includeInMenu': 1
            }}
            category_response = self.callMagentoApi(
                baseUrl=connection.get('url', ''),
                url='/V1/categories',
                method='post',
                token=connection.get('token', ''),
                data=category_data
            )
            if category_response and category_response.get('id') > 0:
                ecomm_id, status = category_response['id'], 1
            else:
                status, error = 0, 'Category is failed to sync'
        return {'status': status, 'ecomm_id':ecomm_id, 'error':error}

    def update_magento_category(self, update_data, ecomm_id, connection):
        status = connection.get('status', False)
        if status and ecomm_id > 0:
            category_response = self.callMagentoApi(
                baseUrl=connection.get('url', ''),
                url='/V1/categories/' + str(ecomm_id),
                method='put',
                token=connection.get('token', ''),
                data={"category": update_data}
            )
            status = 1 if category_response else 0
        return {'status': status}
