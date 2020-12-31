# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _


class MagentoProductTemplate(models.Model):
    _inherit = 'connector.template.mapping'

    def unlink(self):
        imgObjs = self.mapped('name').product_template_image_ids
        res = super(MagentoProductTemplate, self).unlink()
        if res:
            imgObjs.extra_image_ids.write({'extra_image_id': False, 'magento_product_id': False})
        return res

class MagentoProduct(models.Model):
    _inherit = 'connector.product.mapping'

    def unlink(self):
        imgObjs = self.mapped('name').product_template_image_ids
        res = super(MagentoProduct, self).unlink()
        if res:
            imgObjs.extra_image_ids.write({'extra_image_id': False, 'magento_product_id': False})
        return res