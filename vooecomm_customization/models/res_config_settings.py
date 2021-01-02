# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    day_before_expiry = fields.Integer(string='Number of days before expiry', help="Number of days before expiry")
    alert_before_expiry = fields.Integer(string='Alert days before expiry date', help="Alert days before expiry date")
    remove_before_expiry = fields.Integer(string='Removal days before expiry date', help="Removal days before expiry date")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'day_before_expiry', self.day_before_expiry)
        IrDefault.set('res.config.settings', 'alert_before_expiry', self.alert_before_expiry)
        IrDefault.set('res.config.settings', 'remove_before_expiry', self.remove_before_expiry)
        return True

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
			{
				'day_before_expiry': IrDefault.get('res.config.settings', 'day_before_expiry'),
				'alert_before_expiry': IrDefault.get('res.config.settings', 'alert_before_expiry'),
				'remove_before_expiry': IrDefault.get('res.config.settings', 'remove_before_expiry')
			}
		)
        return res
