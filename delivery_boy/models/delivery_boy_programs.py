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

from odoo import models,fields,exceptions,api, _

class DeliveryBoyPrograms(models.Model):
    _name="delivery.boy.programs"
    _description = "delivery boy programs model"

    name = fields.Char(required=True)
    commission_type = fields.Selection(selection=[('ppo','Pay Per Order'),('ppp','Pay Per Product')], required=True)
    matrix_type = fields.Selection(selection=[('fix','Fixed'),('percent','Percentage')], required=True)
    commission_amount = fields.Float(string="Amount", required=True)
    currency_id = fields.Many2one(
                    'res.currency',
                    'Currency',
                    default=lambda self: self.env.user.company_id.currency_id.id
                    )
    is_default = fields.Boolean()

    def unlink(self):
        for program in self:
            if program.is_default:
                raise exceptions.UserError(_("You can't delete the Default Delivery Boy Program."))
            super('DeliveryBoyPrograms', self).unlink()
