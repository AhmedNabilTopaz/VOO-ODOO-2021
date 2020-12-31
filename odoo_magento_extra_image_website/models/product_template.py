# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def write(self, vals):
        moduleMS = self.env['ir.module.module'].search(
            [("name","=","odoo_magento_multi_instance"),("state","=","installed")])
        ctx = dict(self._context or {})
        mapTemplModel = self.env['connector.template.mapping']
        mapProdModel = self.env['connector.product.mapping']

        if moduleMS:
            for obj in self:
                mappedObjs = mapTemplModel.search(
                    [("template_name","=", obj.id),("default_instance","=",True)])
                if mappedObjs:
                    ctx['instance_id'] = mappedObjs[0].instance_id.id
        else:
            activeConn = self.env['connector.instance'].search([('active','=',True)])
            if activeConn:
                ctx['instance_id'] = activeConn[0].id

        if 'product_image_ids' in  vals:
            imgBefore = self.product_image_ids.ids
        res = super(ProductTemplate, self).write(vals)
        if 'product_image_ids' in  vals:
            imgAfter = self.product_image_ids.ids
            imgNeedDel = list(set(imgBefore) - set(imgAfter))
            if imgNeedDel:
                imgNeedDelObjs = self.env['product.image'].browse(imgNeedDel)
                imgNeedDelObjs.unlink()
            for templobj in self:
                if 'magento' not in  ctx:
                    for vrntObj in templobj.product_variant_ids: 
                        mapObj = mapProdModel.search(
                            [("pro_name","=",vrntObj.id) ,("instance_id","=",ctx.get('instance_id', False))])
                        if mapObj:
                            connection = self.env['connector.instance'].with_context(ctx)._create_connection()
                            if connection:
                                url = connection[0]
                                token = connection[1]
                                mageId = mapObj[0].mag_product_id
                                sku = vrntObj.default_code
                                prodImageObjs = vrntObj.product_image_ids
                                productImage = templobj.image
                                self.env['connector.snippet']._export_update_product_extra_images(
                                    prodImageObjs, sku, mageId, url, token)
        return res
