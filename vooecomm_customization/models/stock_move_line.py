# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from datetime import timedelta
from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    cost_price = fields.Float(string='Cost', help="Cost Price for Stock Move Line")
    end_life_date = fields.Date(string='End of life date')
    alert_date = fields.Date(string='Alert Date')
    removable_date = fields.Date(string='Removable date')

    @api.onchange('end_life_date')
    def onchange_end_life_date(self):
        values = self.env['res.config.settings'].sudo().get_values()
        day_before_expiry = values.get('day_before_expiry', False)
        day_before_expiry = day_before_expiry if day_before_expiry else self.product_id.day_before_expiry
        end_life_date = self.end_life_date
        if day_before_expiry and end_life_date:
            date_diff = end_life_date - fields.Date.today()
            if date_diff.days <= day_before_expiry:
                self.end_life_date = ''
                self.alert_date = ''
                self.removable_date = ''
                warning_mess = {
                    'title': _('Validation Error !!'),
                    'message' : _("Expiration date should be greater than current date."),
                }
                return {'warning': warning_mess}
            else:
                self.alert_date = end_life_date - timedelta(days=values.get('alert_before_expiry', 0))
                self.removable_date = end_life_date - timedelta(days=values.get('remove_before_expiry', 0))
                lot_num = self.lot_id.name
                if lot_num:
                    lot_objs = self.env['stock.production.lot'].search([('name', '=',lot_num), ('product_id', '=',self.product_id.id)])
                    if lot_objs and lot_objs.cost_price <= 0.0:
                        lot_objs.cost_price = self.cost_price


        
