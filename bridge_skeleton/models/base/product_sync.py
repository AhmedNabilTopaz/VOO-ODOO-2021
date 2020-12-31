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

    def sync_ecomm_product(self, exup_product_objs, channel, instance_id, sync_opr, connection):
        """
            @method       : export_ecomm_product\n
            @description  : Method helps to export products from Odoo to other ecommerce channel\n
            @params:
                $self               : Current Object
                $exup_product_objs  : List of internal products objects.
                $ctx                : Context of correct class.
                $connection         : Data related to ecommerce instance.
            @response     : Export success/error message.
        """
        success_ids, failed_ids, response_text, action = [], [], '', 'b'
        if sync_opr == 'export':
            for exup_product_obj in exup_product_objs:
                if exup_product_obj.type == 'service':
                    failed_ids.append(exup_product_obj.id)
                    continue
                if hasattr(self, '_export_%s_specific_template' % channel):
                    response = getattr(self, '_export_%s_specific_template' % channel)(exup_product_obj, instance_id, channel, connection)
                    success_ids.append(exup_product_obj.id) if response.get('status', False) else failed_ids.append(response.get('error', False))
        else:
            action = 'c'
            for exup_product_obj in exup_product_objs:
                if hasattr(self, '_update_%s_specific_template' % channel):
                    response = getattr(self, '_update_%s_specific_template' % channel)(exup_product_obj, instance_id, channel, connection)
                    success_ids.append(exup_product_obj.id) if response.get('status', False) else failed_ids.append(response.get('error', False))
        if success_ids:
            text = "\nThe Listed product ids {} has been {} on {}.".format(sorted(success_ids), sync_opr, channel)
            response_text = "{}\n {}".format(response_text, text)
            self.env['connector.sync.history'].create({
                    'status': 'yes',
                    'action_on': 'product',
                    'instance_id':instance_id,
                    'action': action,
                    'error_message': text
            })
        if failed_ids:
            text = "\nThe Listed product ids {} have not been {} on {}.".format(sorted(failed_ids), sync_opr, channel)
            response_text = "{}\n {}".format(response_text, text)
            self.env['connector.sync.history'].create({   
                    'status': 'no',
                    'action_on': 'product',
                    'instance_id':instance_id,
                    'action': action,
                    'error_message': text
            })
        return response_text
