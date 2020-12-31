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

    @api.model
    def get_map_updt_attribute_objs(self, instance_id):
        attribute_map_objs = self.env['connector.attribute.mapping'].search([('instance_id', '=', instance_id)])
        map_dict = dict(attribute_map_objs.mapped(lambda map_obj: \
                (map_obj.odoo_id, {'ecomm_id':map_obj.ecomm_id, 'ecomm_attribute_code':map_obj.ecomm_attribute_code})))
        return map_dict

    def sync_ecomm_attribute(self, connection):
        response_text, attribute_count = '', 0
        attribute_objs = self.env['product.attribute'].search([])
        if attribute_objs:
            ctx = dict(self._context or {})
            instance_id = ctx.get('instance_id', 0)
            channel = ctx.get('ecomm_channel', False)
            map_dict = self.get_map_updt_attribute_objs(instance_id)
            for attribute_obj in attribute_objs:
                response_text, attribute_count = self.start_sync_oprations(attribute_obj, map_dict, channel, instance_id, connection, response_text=response_text, attribute_count=attribute_count)
        else:
            response_text = "No Attribute(s) Found To Be Export!!!"
        if attribute_count:
            response_text = "{}\n {} Attribute(s) and their value(s) successfully Synchronized".format(response_text, attribute_count)
        return response_text

    def start_sync_oprations(self, attribute_obj, map_dict, channel, instance_id, connection, **kwrgs):
        response_text, attribute_count = kwrgs.get('response_text', ''), int(kwrgs.get('attribute_count', 0))
        odoo_id = attribute_obj.id
        name = attribute_obj.name
        ecomm_id, count = 0, 0
        if odoo_id not in map_dict.keys():
            if hasattr(self, 'create_%s_product_attribute' % channel):
                ecomm_attribute_code = name.lower().replace(" ", "_").replace("-", "_")[:29]
                ecomm_attribute_code = ecomm_attribute_code.strip()
                response = getattr(self, 'create_%s_product_attribute' % channel)(name, odoo_id, connection, ecomm_attribute_code)
                if response.get('status', False):
                    ecomm_id = response.get('ecomm_id', 0)
                    if ecomm_id:
                        self.create_odoo_connector_mapping('connector.attribute.mapping', ecomm_id, odoo_id, instance_id, ecomm_attribute_code=ecomm_attribute_code)
                        self.create_ecomm_connector_mapping('connector.attribute.mapping', channel, {'ecomm_id':ecomm_id, 'odoo_id':odoo_id, 'name':ecomm_attribute_code, 'created_by': 'odoo'}, connection)
                else:
                    response_text = "{}{}".format(response_text, response.get('error', ''))
        else:
            map_data = map_dict.get(odoo_id, {})
            ecomm_id = map_data.get('ecomm_id', 0)
            ecomm_attribute_code = map_data.get('ecomm_attribute_code', '')
        if ecomm_id:
            if hasattr(self, 'create_%s_product_attribute_value' % channel):
                getattr(self, 'create_%s_product_attribute_value' % channel)(ecomm_id, attribute_obj, ecomm_attribute_code, instance_id, connection)
            attribute_count += 1
        return response_text, attribute_count
