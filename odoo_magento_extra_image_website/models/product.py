# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import binascii
from urllib.parse import quote
import requests

from odoo import api, fields, models

from odoo import api, fields, models, _


class ProductImage(models.Model):
    _inherit = 'product.image'

    @api.model
    def create_image(self, mageProdId, odooProdId, imageList):
        productObj = self.env['product.product'].browse(odooProdId)
        imgTypeModel = self.env['connector.product.image.type']
        productTemplId = productObj.product_tmpl_id.id
        ctx = dict(self._context) or {}
        
        imgExist = self.env['connector.extra.image'].search([('magento_product_id', '=' , mageProdId), ('instance_id', '=' , ctx.get('instance_id', False))]).image_id.ids
        imgIds = []
        if odooProdId and mageProdId:
            for data in imageList:
                if 'types' in data:
                    imgTypes = data.get('types')
                    imgTypeIds = []
                    for typ in imgTypes:
                        existTypes = imgTypeModel.search([('name','=',typ)])
                        if existTypes:
                            imgTypeIds.append(existTypes[0].id)
                        else:
                            imgTypeIds.append(imgTypeModel.create({'name':typ}).id)
                    data.pop('types')
                extraImageIds = {}
                extraImageId = data.pop('extra_image_id', False)
                extraImageIds['extra_image_id'] = extraImageId
                extraImageIds['magento_product_id'] = mageProdId
                extraImageIds['magento_image_type'] = imgTypeIds
                extraImageIds['instance_id'] = ctx.get('instance_id', False)
                data['extra_image_ids'] = [(0, 0, extraImageIds)]
                existImage = self.env['connector.extra.image'].search([('magento_product_id', '=' , mageProdId), ('extra_image_id', '=' , extraImageId), ('instance_id', '=' , ctx.get('instance_id', False))]).image_id.ids
                imageUrl = data.pop('image_url', False)
                if not existImage:
                    if imageUrl:
                        proImage = binascii.b2a_base64(requests.get(imageUrl).content)
                        data['image_1920'] = proImage
                        if not data.get('name'):
                            data['name'] = data.get('mage_file')
                        data.update(product_tmpl_id = productTemplId)
                        imgIds.append(self.create(data).id)
                else:
                    imgIds.append(existImage[0])
            imgNeedDel = list(set(imgExist) - set(imgIds))
            if imgNeedDel:
                imgNeedDelObjs = self.browse(imgNeedDel)
                imgNeedDelObjs.unlink()
            return True
        return False

    def unlink(self):
        ctx = dict(self._context) or {}
        mapProdModel = self.env['connector.product.mapping']
        if 'magento' not in ctx:
            connection = self.env['connector.instance']._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]
                autoImage = connection[3]
                if autoImage == 'Yes':
                    for imgObj in self:
                        if imgObj.read([]):
                            mageImgId = imgObj.mage_image_id or False
                            mageProdId = imgObj.mage_product_id or False
                            mapObj = mapProdModel.search([('magento_product_id', '=', mageProdId)])
                            prodObj = mapObj.pro_name
                            productSku = prodObj.default_code
                            try:
                                productSku = quote(productSku, safe='')
                            except Exception as e:
                                productSku = quote(productSku.encode("utf-8"), safe='')
                            if mageImgId and mageProdId:
                                try :
                                    productUrl = url + "/index.php/rest/V1/products/" + \
                                        productSku + "/media/" + str(mageImgId)
                                    token = token.replace('"', "")
                                    headers = {'Authorization': token,
                                   'Content-Type': 'application/json'}
                                    imageDelResp = requests.delete(
                                        productUrl, headers=headers)
                                except Exception as e:
                                    pass
        return super(ProductImage, self).unlink()