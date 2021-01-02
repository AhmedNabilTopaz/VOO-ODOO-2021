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

class InheritResUsers(models.Model):
    _inherit="res.users"

    is_delivery_boy = fields.Boolean(string="Is a Delivery Boy", copy=False, related='partner_id.is_delivery_boy')

    def toggle_is_delivery_boy(self):
        for user in self:
            if self.is_delivery_boy:
                self.partner_id.is_delivery_boy = False
            else:
                self.partner_id.is_delivery_boy = True
