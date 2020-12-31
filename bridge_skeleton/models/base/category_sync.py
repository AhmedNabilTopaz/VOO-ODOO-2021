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

    def sync_ecomm_category(self, exp_category_objs, channel, instance_id, sync_opr, connection):
        """
            @method       : sync_ecomm_category\n
            @description  : Method helps to export categories from Odoo to other ecommerce channel\n
            @params:
                $self           : Current Object
                $exp_category_objs  : List of internal categories objects.
                $ctx            : Context of correct class.
                $connection     : Data related to ecommerce instance.
            @response     : Export success/error message.
        """
        success_ids, failed_ids, response_text, action = [], [], '', 'b'
        if sync_opr == 'export':
            for exp_category_obj in exp_category_objs:
                categ_id = self.sync_categories(exp_category_obj, instance_id, channel, connection)
                success_ids.append(exp_category_obj.id) if categ_id else failed_ids.append(exp_category_obj.id)
        else:
            action = 'c'
            success_ids, failed_ids, updted_category_mapping_ids = self._update_specific_category(exp_category_objs, channel, instance_id, connection)
            if success_ids:
                self.update_odoo_mapping('connector.category.mapping', updted_category_mapping_ids, {'need_sync':'No'})
        if success_ids:
            text = "\nThe Listed category ids {} has been {} on {}.".format(sorted(success_ids), sync_opr, channel)
            response_text = "{}\n {}".format(response_text, text)
            self.env['connector.sync.history'].create({
                    'status': 'yes',
                    'action_on': 'category',
                    'instance_id':instance_id,
                    'action': action,
                    'error_message': text
            })
        if failed_ids:
            text = "\nThe Listed category ids {} have not been {} on {}.".format(sorted(failed_ids), sync_opr, channel)
            response_text = "{}\n {}".format(response_text, text)
            self.env['connector.sync.history'].create({   
                    'status': 'no',
                    'action_on': 'category',
                    'instance_id':instance_id,
                    'action': action,
                    'error_message': text
            })
        return response_text

    @api.model
    def sync_categories(self, category_obj, instance_id, channel, connection):
        if category_obj:
            mapped_category_objs = category_obj.connector_mapping_ids.filtered(lambda obj: obj.instance_id.id == instance_id)
            if not mapped_category_objs:
                parent_categ_id = self.sync_categories(category_obj.parent_id, instance_id, channel, connection) if category_obj.parent_id else 1
                if hasattr(self, 'create_%s_category' % channel):
                    name = category_obj.name
                    odoo_id = category_obj.id
                    response = getattr(self, 'create_%s_category' % channel)(odoo_id, parent_categ_id, name, connection)
                    if response.get('status', False):
                        ecomm_id = response.get('ecomm_id', 0)
                        if ecomm_id:
                            self.create_odoo_connector_mapping('connector.category.mapping', ecomm_id, odoo_id, instance_id)
                            self.create_ecomm_connector_mapping('connector.category.mapping', channel, {'ecomm_id':ecomm_id, 'odoo_id':odoo_id, 'created_by': 'odoo'}, connection)
                        return ecomm_id
            else:
                return mapped_category_objs[0].ecomm_id
        return False
    
    def _update_specific_category(self, updt_map_objs, channel, instance_id, connection):
        updted_category_ids, not_updted_category_ids, updted_category_mapping_ids, = [], [], []
        for categ_map_obj in updt_map_objs:
            categ_obj = categ_map_obj.name
            ecomm_id = categ_map_obj.ecomm_id
            if categ_obj and ecomm_id:
                ecomm_cat_parent_id = self.get_ecomm_parent_id(categ_obj, instance_id, channel, connection)
                if hasattr(self, 'update_%s_category' % channel):
                    response = getattr(self, 'update_%s_category' % channel)({'name': categ_obj.name, 'parent_id': ecomm_cat_parent_id}, ecomm_id, connection)
                    if response.get('status', False):
                        updted_category_ids.append(categ_obj.id)
                        updted_category_mapping_ids.append(categ_map_obj.id)
                        self.update_ecomm_connector_mapping('connector.category.mapping', channel, {'ecomm_id':ecomm_id, 'name':categ_obj.name, 'created_by': 'odoo'}, connection)
                    else:
                        not_updted_category_ids.append(categ_obj.id)
            else:
                not_updted_category_ids.append(categ_obj.id)
        return updted_category_ids, not_updted_category_ids, updted_category_mapping_ids

    def get_ecomm_parent_id(self, categ_obj, instance_id, channel, connection):
        ecomm_cat_parent_id = 1
        if categ_obj.parent_id:
            parent_category_obj = categ_obj.parent_id.connector_mapping_ids.filtered(lambda obj: obj.instance_id.id == instance_id)
            if parent_category_obj:
                ecomm_cat_parent_id = parent_category_obj[0].ecomm_id
            else:
                ecomm_cat_parent_id = self.sync_categories(
                    parent_category_obj, instance_id, channel, connection)
        return ecomm_cat_parent_id
