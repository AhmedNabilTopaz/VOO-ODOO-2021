# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import codecs
import io
import logging

from PIL import Image
from odoo import api, fields, models, _

_logger = logging.getLogger('__product_sync__')


class MagentoSynchronization(models.TransientModel):
    _inherit = 'connector.snippet'

    #############################################
    ##  Inherited export Specific product sync ##
    #############################################

    def _get_product_array(self, instance_id, channel, prod_obj, get_product_data, connection):
        getProductData = super(MagentoSynchronization, self)._get_product_array(
                instance_id, channel, prod_obj, get_product_data, connection)
        mediaGalleryEntries = getProductData.get('media_gallery_entries', [])
        ctx = dict(self._context or {})
        if prod_obj._name == 'product.product':
            prodImageObjs = prod_obj.product_template_image_ids
        else:
            prodImageObjs = prod_obj.product_template_image_ids
        for imgObj in prodImageObjs:
            image_id = imgObj.extra_image_ids.filtered(lambda obj : obj.instance_id.id == ctx.get('instance_id')).extra_image_id
            if image_id:
                imageData = self._get_image_data(imgObj)
                if imageData:
                    imageData.update(
                        id=str(image_id)
                    )
                mediaGalleryEntries.append(imageData)
        getProductData.update(media_gallery_entries=mediaGalleryEntries)
        return getProductData

    @api.model
    def _export_magento_specific_template(self,  vrnt_obj, instance_id, channel, connection):
        pro = super(MagentoSynchronization, self)._export_magento_specific_template(
            vrnt_obj, instance_id, channel, connection)
        url = connection.get('url', '')
        token = connection.get('token', '')
        if pro and pro.get('status'):
            tmpl_extra_image = vrnt_obj.product_template_image_ids
            product_image = vrnt_obj.image_1920
            if vrnt_obj.attribute_line_ids:
                sku = vrnt_obj.default_code
                self._export_update_product_extra_images(
                    tmpl_extra_image, sku, pro.get('ecomm_id'), url, token, product_image)
        return pro

    @api.model
    def _export_specific_product(self, vrnt_obj, template_sku, instance_id, channel, url, token, connection):
        pro = super(MagentoSynchronization, self)._export_specific_product(
            vrnt_obj, template_sku, instance_id, channel, url, token, connection) 
        if pro and pro.get('id'):
            images = vrnt_obj.product_template_image_ids
            product_image = vrnt_obj.image_1920
            sku = vrnt_obj.default_code
            self._export_update_product_extra_images(
                images, sku, pro.get('id'), url, token, product_image)
        return pro

    def _update_magento_specific_template(self, temp_obj, instance_id, channel, connection):
        pro = super(MagentoSynchronization, self)._update_magento_specific_template(
            temp_obj, instance_id, channel, connection)
        url = connection.get('url', '')
        token = connection.get('token', '')
        if pro and pro.get('status'):
            temp_id = temp_obj.name
            if temp_id.attribute_line_ids:
                mage_id = temp_obj.ecomm_id
                image_1920 = temp_id.image_1920
                product_image = temp_id.product_template_image_ids
                sku = temp_id.default_code
                self._export_update_product_extra_images(
                    product_image, sku, mage_id, url, token, image_1920)
        return pro

    def _update_specific_product(self, prod_map_obj, url, token, channel, connection):
        pro = super(MagentoSynchronization, self)._update_specific_product(
            prod_map_obj, url, token, channel, connection)
        if pro and pro[0] != 0:
            pro = prod_map_obj.name
            mage_id = prod_map_obj.ecomm_id
            image_1920 = pro.image_1920
            product_image = pro.product_template_image_ids
            sku = pro.default_code
            self._export_update_product_extra_images(
                product_image, sku, mage_id, url, token, image_1920)
        return pro

    ################# update extra image ###################

    def _get_image_data(self, img_obj):
        pro_image = img_obj.image_1920
        if pro_image:
            if not img_obj.position :
                img_obj.position = str(100 + img_obj.id)
            image_stream = io.BytesIO(codecs.decode(pro_image, 'base64'))
            mob_image = Image.open(image_stream)
            image_type = mob_image.format.lower()
            if not image_type:
                image_type = 'jpeg'
            mage_image_type = "image/" + image_type
            imageData = {
                'media_type': 'image',
                'label': img_obj.name or '',
                'position': img_obj.position,
                'disabled': False,
                'types': img_obj.extra_image_ids.magento_image_type.mapped('name'),
                'content': {
                    'base64_encoded_data': pro_image.decode("utf-8"), 
                    'type': mage_image_type, 
                    'name': "product_additional_image_"+str(img_obj.id)
                }
            }
            return imageData
        else :
            return False

    @api.model
    def _export_update_product_extra_images(self, images, sku, mage_id, url, token, product_image):
        response = True
        ctx = dict(self._context or {})
        for img_obj in images:
            if img_obj.extra_image_ids.filtered(lambda obj : obj.instance_id.id == ctx.get('instance_id')):
                if not img_obj.extra_image_ids.extra_image_id:
                    image_data = self._get_image_data(img_obj)
                    try:
                        prod_image_data = {"entry": image_data}
                        prod_response = self.callMagentoApi(
                            url='/V1/odoomagento_extraimage/products/' + str(mage_id) + "/media",
                            method='post',
                            token=token,
                            data=prod_image_data,
                            baseUrl=url
                        )
                        if prod_response:
                            img_obj.extra_image_ids.write({
                                'extra_image_id': int(prod_response),
                                'magento_product_id': mage_id
                            })
                    except Exception as e:
                        response = False
        return response
