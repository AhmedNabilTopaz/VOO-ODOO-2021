# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

######################## Mapping update Model(Used from server action) ###


class MappingUpdate(models.TransientModel):
    _name = "mapping.update"
    _description = "Mapping Update"

    need_sync = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Update Required')

    @api.model
    def open_update_wizard(self):
        partial = self.create({})
        return {'name': ("Bulk Action"),
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'mapping.update',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': self._context,
                'domain': '[]',
                }

    def update_mapping_status(self):
        active_ids, status = self._context.get('active_ids'), self.need_sync
        self.env[self._context.get('active_model')].browse(active_ids).write({'need_sync':status})
        text = "Status of {} record has been successfully updated to {}.".format(len(active_ids), status)
        return self.env['message.wizard'].genrated_message(text)
