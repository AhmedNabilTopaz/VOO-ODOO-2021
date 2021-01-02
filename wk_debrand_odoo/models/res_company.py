# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

import os
from odoo import api, models, tools

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def reset_company_logo(self):
        order_objs = self.search([])
        for order_obj in order_objs:
            order_obj.logo = open(os.path.join(tools.config['root_path'], 'addons', 'base', 'res', 'res_company_logo.png'), 'rb') .read().encode('base64')

    
    def get_logo_data_url(self):
        url=image_data_uri(self.logo)
        return url