# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


class WkSkeleton(models.TransientModel):
    _inherit = "wk.skeleton"
    _description = " Skeleton for all XML RPC imports in Odoo"

    @api.model
    def get_ecomm_href(self, getcommtype=False):
        href_list = super(WkSkeleton, self).get_ecomm_href(getcommtype)
        href_list = {}
        if getcommtype=='magento':
            href_list = {
                'user_guide':'https://webkul.com/blog/magento-openerp-bridge/',
                'rate_review':'https://store.webkul.com/Magento-OpenERP-Bridge.html#tabreviews',
                'extension':'https://store.webkul.com/Magento-Extensions/ERP.html',
                'name' : 'MAGENTO',
                'short_form' : 'Mob',
                'img_link' : '/odoo_magento_connect/static/src/img/magento-logo.png'
            }
        return href_list
