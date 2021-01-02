# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import logging
_logger = logging.getLogger(__name__)

from odoo import models,fields,api, _

class ResConfigSettings(models.TransientModel):
    _inherit="res.config.settings"

    db_config_id = fields.Many2one(comodel_name='delivery.boy.config', config_parameter="delivery_boy.db_config_id")
    allow_db_program = fields.Boolean(config_parameter="delivery_boy.allow_db_program")
    db_program_id = fields.Many2one(comodel_name='delivery.boy.programs', string="Program", config_parameter="delivery_boy.db_program_id")
    auto_validate = fields.Boolean(config_parameter="delivery_boy.auto_validate")
    auto_invoice = fields.Boolean(config_parameter="delivery_boy.auto_invoice")
    verify_token = fields.Boolean(related="db_config_id.verify_token", readonly=False)
    delivery_token_mail_temp_id = fields.Many2one(comodel_name="mail.template", config_parameter="delivery_boy.delivery_token_mail_temp_id")


    @api.model
    def get_db_configuration(self):
        params = self.env['ir.config_parameter'].sudo()
        config = {
        'program': self.env['delivery.boy.programs'].sudo().browse(int(params.get_param('delivery_boy.db_program_id'))) or False,
        'allow_db_program': params.get_param('delivery_boy.allow_db_program') and True or False,
        'auto_validate': params.get_param('delivery_boy.auto_validate') and True or False,
        'auto_invoice': params.get_param('delivery_boy.auto_invoice') and True or False,
        'verify_token': self.env['delivery.boy.config'].sudo().search([], limit=1).verify_token,
        'delivery_token_mail_temp_id': self.env['mail.template'].sudo().browse(int(params.get_param('delivery_boy.delivery_token_mail_temp_id'))) or False,
        }
        return config

    def open_delivery_boy_conf(self):
        response = {}

        params = self.env['ir.config_parameter'].sudo()
        db_config_id = params.get_param('delivery_boy.db_config_id') or False
        if db_config_id:
            response.update({'res_id': int(db_config_id)})

        response.update({
        'type': 'ir.actions.act_window',
        'name': 'Delivery Boy Configuration',
        'view_mode': 'form',
        'res_model': 'delivery.boy.config',
        'target': 'current'
        })

        return response
