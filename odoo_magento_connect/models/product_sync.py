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
from urllib.parse import quote

from PIL import Image

from odoo import _, api, models
from odoo.exceptions import UserError


class ConnectorSnippet(models.TransientModel):
    _inherit = "connector.snippet"

    def _create_product_attribute_option(self, wk_attr_line_objs):
        options_data = []
        ctx = dict(self._context or {})
        attr_val_map_model = self.env['connector.option.mapping']
        for type_obj in wk_attr_line_objs:
            get_product_option_data = {}
            mage_attr_ids = self.with_context(
                ctx)._check_attribute_sync(type_obj)
            if not mage_attr_ids :
                continue
            get_product_option_data['attribute_id'] = mage_attr_ids[0]
            get_product_option_data['label'] = type_obj.attribute_id.name
            get_product_option_data['position'] = 0
            get_product_option_data['isUseDefault'] = True
            get_product_option_data['values'] = []
            for value_id in type_obj.value_ids.ids:
                type_search = attr_val_map_model.search(
                    [('name', '=', value_id)], limit=1)
                if type_search:
                    get_product_option_data['values'].append(
                        {"value_index": type_search.ecomm_id})
            options_data.append(get_product_option_data)
        return options_data

    ############# check single attribute lines ########
    def _search_single_values(self, templ_id, attr_id):
        dic = {}
        attr_line_obj = self.env['product.template.attribute.line'].search(
            [('product_tmpl_id', '=', templ_id), ('attribute_id', '=', attr_id)], limit=1)
        if attr_line_obj and len(attr_line_obj.value_ids) == 1:
            dic[attr_line_obj.attribute_id.name] = attr_line_obj.value_ids.name
        return dic

    ############# check attributes syned return mage attribute ids ########
    def _check_attribute_sync(self, attr_line_obj):
        mage_attribute_ids = []
        ecomm_id = self.env['connector.attribute.mapping'].search(
            [('name', '=', attr_line_obj.attribute_id.id)], limit=1).ecomm_id
        if ecomm_id:
            mage_attribute_ids.append(ecomm_id)
        return mage_attribute_ids

    ############# check attributes lines and set attributes are same ########
    def _check_attribute_with_set(self, attr_set_obj, attr_line_objs):
        set_attr_objs = attr_set_obj.attribute_ids
        if not set_attr_objs:
            return {'status': 0, 'error': str(attr_set_obj.name) + ' Attribute Set Name has no attributes!!!'}
        set_attr_list = list(set_attr_objs.ids)
        for attr_line_obj in attr_line_objs:
            if attr_line_obj.attribute_id.id not in set_attr_list:
                return {'status': 0, 'error': str(attr_set_obj.name) + ' Attribute Set Name not matched with attributes!!!'}
        return {'status': 1}

    def _check_valid_attribute_set(self, attr_set_obj, templateId, instance_id):
        if instance_id and instance_id == attr_set_obj.instance_id.id:
            return attr_set_obj
        return False

    @api.model
    def get_default_attribute_set(self, instance_id):
        default_attrset = self.env['magento.attribute.set'].search(
            [('set_id', '=', 4), ('instance_id', '=', instance_id)], limit=1)
        if not default_attrset:
            raise UserError(
                _('Information!\nDefault Attribute set not Found, please sync all Attribute set from Magento!!!'))
        return default_attrset

    @api.model
    def get_magento_attribute_set(self, attribute_line_objs, instance_id):
        flag = False
        template_attribute_ids = []
        for attr in attribute_line_objs:
            template_attribute_ids.append(attr.attribute_id.id)
        attr_set_objs = self.env['magento.attribute.set'].search(
            [('instance_id', '=', instance_id)], order="set_id asc")
        for attr_set_obj in attr_set_objs:
            common_attributes = sorted(
                set(attr_set_obj.attribute_ids.ids) & set(template_attribute_ids))
            template_attribute_ids.sort()
            if common_attributes == template_attribute_ids:
                return attr_set_obj
        return False

    @api.model
    def assign_attribute_Set(self, exup_product_obj, attribute_line_objs, instance_id):
        set_obj = self.get_default_attribute_set(instance_id)
        if attribute_line_objs:
            set_obj = self.get_magento_attribute_set(
                attribute_line_objs, instance_id)
        if set_obj:
            exup_product_obj.write({'attribute_set_id': set_obj.id})
        else:
            return False
        return True

    ############# sync template variants ########
    def _sync_template_variants(self, template_obj, template_sku, instance_id, channel, url, token, connection):
        mage_variant_ids = []
        ctx = dict(self._context or {})
        for vrnt_obj in template_obj.product_variant_ids:
            exist_map_obj = vrnt_obj.connector_mapping_ids.filtered(lambda obj: obj.instance_id.id == instance_id)
            if exist_map_obj:
                mage_variant_ids.append(exist_map_obj[0].ecomm_id)
            else:
                mage_vrnt_id = self._export_specific_product(
                    vrnt_obj, template_sku, instance_id, channel, url, token, connection)
                if mage_vrnt_id and mage_vrnt_id.get('id'):
                    mage_variant_ids.append(mage_vrnt_id['id'])
        return mage_variant_ids

    def _get_product_media(self, prod_obj):
        pro_image = prod_obj.image_1920
        if pro_image:
            image_stream = io.BytesIO(codecs.decode(pro_image, 'base64'))
            image = Image.open(image_stream)
            image_type = image.format.lower()
            if not image_type:
                image_type = 'jpeg'
            magento_image_type = "image/" + image_type
            return {
                'position': 1,
                'media_type': 'image',
                'disabled': False,
                'label': '',
                'types': ["image", "small_image", "thumbnail", "swatch_image"],
                'content': {
                    'base64_encoded_data': pro_image.decode("utf-8"), 
                    'type': magento_image_type, 
                    'name': 'ProductImage_'+str(prod_obj.id)
                }
            }
        return False

    ############# fetch product details ########
    def _get_product_array(self, instance_id, channel, prod_obj, get_product_data, connection):
        prod_categs = []
        for extra_cat_obj in prod_obj.connector_categ_ids.filtered(lambda obj: obj.instance_id.id == instance_id):
            for category_obj in extra_cat_obj.categ_ids:
                mage_categ_id = self.sync_categories(category_obj, instance_id, channel, connection)
                if mage_categ_id:
                    prod_categs.append(mage_categ_id)
        status = 2
        if prod_obj.sale_ok:
            status = 1
        get_product_data.update(
            name=prod_obj.name,
            weight=prod_obj.weight or 0.00,
            status=status
        )
        custom_attributes = [
            {"attribute_code": "description", "value": prod_obj.description},
            {"attribute_code": "short_description", "value": prod_obj.description_sale},
            {"attribute_code": "category_ids", "value": prod_categs},
            {"attribute_code": "cost", "value": prod_obj.standard_price or 0.00}
        ]
        if 'custom_attributes' not in get_product_data :
            get_product_data['custom_attributes'] = custom_attributes
        else :
            get_product_data['custom_attributes'] += custom_attributes
        image_data = self._get_product_media(prod_obj)
        if image_data:
            get_product_data.update(media_gallery_entries=[image_data])
        return get_product_data
    
    def _get_product_qty(self, prod_obj, instance_id, stock_item_id=False, stock_id=1):
        mob_stock_action = self.env['connector.instance'].sudo().browse(instance_id).connector_stock_action
        product_qty = prod_obj.qty_available - prod_obj.outgoing_qty if mob_stock_action and mob_stock_action == "qoh" else prod_obj.virtual_available
        stock_data = {
            'stock_id': 1,
            'qty': product_qty,
            'is_in_stock': True if product_qty else 0
        }
        if stock_item_id :
            stock_data.update(itemId=stock_item_id)
        return stock_data

    #############################################
    ##          single products create         ##
    #############################################

    def prodcreate(self, url, token, vrnt_obj, prodtype, sku, get_product_data, instance_id):
        stock = 0
        quantity = 0
        odoo_id = vrnt_obj.id
        product_data = {"product": get_product_data}
        prod_response = self.callMagentoApi(
            baseUrl=url,
            url='/V1/products',
            method='post',
            token=token,
            data=product_data
        )
        if prod_response and prod_response.get('id'):
            ecomm_id = prod_response.get('id')
            self.create_odoo_connector_mapping('connector.product.mapping', ecomm_id, odoo_id, instance_id, magento_stock_id=prod_response['extension_attributes']['stock_item']['item_id'])
            mapData = {'product': {'magento_id': ecomm_id, 'odoo_id': odoo_id, 'created_by': 'Odoo'}}
            mapResponse = self.callMagentoApi(
                baseUrl=url,
                url='/V1/odoomagentoconnect/product',
                method='post',
                token=token,
                data=mapData
            )
            instanceObj = self.env['connector.instance'].browse(instance_id)
            warehouseData = self.env['stock.move'].with_context(connector_stock_action=instanceObj.connector_stock_action).getWarehouseArray(odoo_id, ecomm_id)
            self.env['stock.move'].synch_warehouse_quantity(ecomm_id, warehouseData, instanceObj)
        return prod_response

    #############################################
    ##          Specific product sync          ##
    #############################################
    def _export_specific_product(self, vrnt_obj, template_sku, instance_id, channel, url, token, connection):
        """
        @param code: product Id
        @param context: A standard dictionary
        @return: list
        """
        get_product_data = {}
        if vrnt_obj:
            custom_attributes = []
            sku = vrnt_obj.default_code or 'Ref %s' % vrnt_obj.id
            prod_visibility = 4 if template_sku == "single_variant" else 1
            prodtype = 'simple' if vrnt_obj.type in ['product', 'consu'] else 'virtual'
            for temp_value_obj in vrnt_obj.product_template_attribute_value_ids:
                value_obj = temp_value_obj.product_attribute_value_id
                ecomm_attribute_code = self.env['connector.attribute.mapping'].search(
                    [('name', '=', value_obj.attribute_id.id)],limit=1).ecomm_attribute_code or False
                mage_value_id = self.env['connector.option.mapping'].search(
                    [('name', '=', value_obj.id)],limit=1).ecomm_id or 0
                if ecomm_attribute_code and mage_value_id:
                    custom_attributes.append({
                        "attribute_code": ecomm_attribute_code, 
                        "value": mage_value_id
                    })
            custom_attributes.append({"attribute_code": 'tax_class_id', "value": 0}) 
            stock_data = self._get_product_qty(vrnt_obj, instance_id)
            extension_attributes = {'stock_item': stock_data}
            get_product_data.update(
                attribute_set_id=vrnt_obj.product_tmpl_id.attribute_set_id.set_id,
                type_id=prodtype,
                visibility=prod_visibility,
                sku=sku,
                price=vrnt_obj.list_price + vrnt_obj.price_extra or 0.00,
                custom_attributes=custom_attributes,
                extension_attributes=extension_attributes
            )
            get_product_data = self._get_product_array(
                instance_id, channel, vrnt_obj, get_product_data, connection)
            vrnt_obj.write({'prod_type': prodtype, 'default_code': sku})
            mag_prod = self.prodcreate(url, token, vrnt_obj,
                                      prodtype, sku, get_product_data, instance_id)
            return mag_prod

    def _export_magento_specific_template(self, exup_product_obj, instance_id, channel, connection):
        status, ecomm_id, error = connection.get('status', False), 0, ''
        if status and exup_product_obj:
            url = connection.get('url', '')
            token = connection.get('token', '')
            mage_set_id = 0
            ctx = dict(self._context or {})
            get_product_data = {}
            template_id = exup_product_obj.id
            template_sku = exup_product_obj.default_code or 'Template Ref %s' % template_id
            if not exup_product_obj.product_variant_ids:
                return {'status': 0, 'error': str(template_id) + ' No Variant Ids Found!!!'}
            else:
                wk_attr_line_objs = exup_product_obj.attribute_line_ids
                if not exup_product_obj.attribute_set_id.id:
                    res = self.assign_attribute_Set(exup_product_obj, wk_attr_line_objs, instance_id)
                    if not res:
                        return {'status': 0, 'error': str(template_id) + ' Attribute Set Name not matched with attributes!!!'}
                attr_set_obj = self.with_context(
                    ctx)._check_valid_attribute_set(exup_product_obj.attribute_set_id, template_id, instance_id)
                if not attr_set_obj:
                    return {'status': 0, 'error': str(template_id) + ' Matching attribute set not found for this instance!!!'}
                if not wk_attr_line_objs:
                    template_sku = 'single_variant'
                    mage_prod_ids = self.with_context(ctx)._sync_template_variants(
                        exup_product_obj, template_sku, instance_id, channel, url, token, connection)
                    name = exup_product_obj.name
                    price = exup_product_obj.list_price or 0.0
                    if mage_prod_ids:
                        ecomm_id = mage_prod_ids[0]
                        self.create_odoo_connector_mapping('connector.template.mapping', ecomm_id, template_id, instance_id, is_variants=False)
                        return {'status': 1, 'ecomm_id': ecomm_id}
                    else:
                        return {'status': 0}
                else:
                    check_attribute = self.with_context(
                        ctx)._check_attribute_with_set(attr_set_obj, wk_attr_line_objs)
                    if not check_attribute.get('status', False):
                        return check_attribute
                    mage_set_id = exup_product_obj.attribute_set_id.set_id
                    if not mage_set_id:
                        return {'status': 0, 'error': str(template_id) + ' Attribute Set Name not found!!!'}
                    else:
                        for attr_line_obj in wk_attr_line_objs:
                            mage_attr_ids = self.with_context(
                                ctx)._check_attribute_sync(attr_line_obj)
                            if not mage_attr_ids:
                                return {'status': 0, 'error': str(template_id) + ' Attribute not syned at magento!!!'}
                            val_dict = self.with_context(ctx)._search_single_values(
                                template_id, attr_line_obj.attribute_id.id)
                            if val_dict:
                                ctx.update(val_dict)
                            domain = [('product_tmpl_id', '=', template_id)]
                        custom_attributes = [dict(attribute_code='tax_class_id',value=0)]
                        mage_prod_ids = self.with_context(ctx)._sync_template_variants(
                            exup_product_obj, template_sku, instance_id, channel, url, token, connection)
                        options_data = self._create_product_attribute_option(
                            wk_attr_line_objs)
                        stock_data = {
                            'is_in_stock': True
                        }
                        extension_attributes = {
                            'configurable_product_links': mage_prod_ids,
                            'configurable_product_options': options_data,
                            'stock_item': stock_data
                        }
                        get_product_data.update(
                            attribute_set_id=mage_set_id,
                            visibility=4,
                            price=exup_product_obj.list_price or 0.00,
                            sku='Template sku %s' % template_id,
                            type_id='configurable',
                            custom_attributes=custom_attributes,
                            extension_attributes=extension_attributes
                        )
                        get_product_data = self.with_context(ctx)._get_product_array(
                            instance_id, channel, exup_product_obj, get_product_data, connection)
                        exup_product_obj.write({'prod_type': 'configurable'})
                        product_data = {"product": get_product_data}
                        prod_response = self.callMagentoApi(
                            baseUrl=url,
                            url='/V1/products',
                            method='post',
                            token=token,
                            data=product_data
                        )
                        if prod_response and prod_response.get('id'):
                            ecomm_id = prod_response['id']
                            self.create_odoo_connector_mapping('connector.template.mapping', ecomm_id, template_id, instance_id, is_variants=True)
                            mapData = {'template': {
                                'magento_id': ecomm_id, 
                                'odoo_id': template_id, 
                                'created_by': 'Odoo'
                            }}
                            mapResponse = self.callMagentoApi(
                                baseUrl=url,
                                url='/V1/odoomagentoconnect/template',
                                method='post',
                                token=token,
                                data=mapData
                            )
                            return {'status': 1, 'ecomm_id': ecomm_id}
                        else:
                            return {'status': 0, 'error': str(template_id) + ' Error during parent sync.'}

    #############################################
    ##          update specific product        ##
    #############################################
    def _update_specific_product(self, prod_map_obj, url, token, channel, connection):
        get_product_data = {}
        prod_obj = prod_map_obj.name
        mage_prod_id = prod_map_obj.ecomm_id
        instance_obj = prod_map_obj.instance_id
        stockItemId = prod_map_obj.magento_stock_id
        attr_map_model = self.env['connector.attribute.mapping']
        attr_val_map_model = self.env['connector.option.mapping']
        if prod_obj and mage_prod_id:
            custom_attributes = []
            for temp_value_obj in prod_obj.product_template_attribute_value_ids:
                value_obj = temp_value_obj.product_attribute_value_id
                ecomm_attribute_code = attr_map_model.search(
                    [('name', '=', value_obj.attribute_id.id)],limit=1).ecomm_attribute_code or False
                mage_value_id = attr_val_map_model.search(
                    [('name', '=', value_obj.id)],limit=1).ecomm_id or 0
                if ecomm_attribute_code and mage_value_id:
                    custom_attributes.append({
                        "attribute_code": ecomm_attribute_code, 
                        "value": mage_value_id
                    })
            get_product_data.update(
                id=mage_prod_id,
                sku=prod_obj.default_code,
                price=prod_obj.list_price + prod_obj.price_extra or 0.00,
                custom_attributes=custom_attributes
            )
            get_product_data = self._get_product_array(
                instance_obj.id, channel, prod_obj, get_product_data, connection)
            if instance_obj.inventory_sync == 'enable':
                stock_data = self._get_product_qty(prod_obj, instance_obj.id)
                extension_attributes = get_product_data.get('extension_attributes', {})
                extension_attributes.update(stock_item=stock_data)
                get_product_data['extension_attributes'] = extension_attributes

            product_data = {"product": get_product_data}
            prod_response = self.callMagentoApi(
                baseUrl=url,
                url="/V1/odoomagentoconnect/products",
                method='post',
                token=token,
                data=product_data
            )
            if prod_response:
                prod_map_obj.need_sync = 'No'
                warehouseData = self.env['stock.move'].with_context(connector_stock_action=instance_obj.connector_stock_action).getWarehouseArray(prod_obj.id, mage_prod_id)
                self.env['stock.move'].synch_warehouse_quantity(mage_prod_id, warehouseData, instance_obj)
            return [1, prod_obj.id]

    def _update_magento_specific_template(self, exup_product_obj, instance_id, channel, connection):
        status, ecomm_id, error = connection.get('status', False), 0, ''
        if status and exup_product_obj:
            url = connection.get('url', '')
            token = connection.get('token', '')
            ctx = dict(self._context or {})
            get_product_data = {}
            temp_obj = exup_product_obj.name
            mage_prod_ids = []
            mage_prod_id = exup_product_obj.ecomm_id
            if temp_obj and mage_prod_id:
                if temp_obj.product_variant_ids:
                    template_sku = temp_obj.default_code or 'Template Ref %s' % temp_obj.id
                    mage_prod_ids = self._sync_template_variants(temp_obj, template_sku, instance_id, channel, url, token, connection)
                    for vrnt_obj in temp_obj.product_variant_ids:
                        prod_map_obj = vrnt_obj.connector_mapping_ids.filtered(lambda obj: obj.instance_id.id == instance_id)
                        if prod_map_obj:
                            self._update_specific_product(prod_map_obj, url, token, channel, connection)
                else:
                    return {'status': 0, 'error': str(temp_obj.id) + ' No Variant Ids Found!!!'}
                if exup_product_obj.is_variants and mage_prod_ids:
                    get_product_data = self._get_product_array(instance_id, channel, temp_obj, get_product_data, connection)
                    options_data = self._create_product_attribute_option(temp_obj.attribute_line_ids)
                    stock_data = {
                        'is_in_stock': True
                    }
                    extension_attributes = get_product_data.get('extension_attributes', {})
                    extension_attributes.update({
                        'configurable_product_links': mage_prod_ids,
                        'configurable_product_options': options_data,
                        'stock_item': stock_data
                    })
                    get_product_data.update(
                        price=temp_obj.list_price or 0.00,
                        extension_attributes=extension_attributes,
                        id=mage_prod_id
                    )
                    product_data = {"product": get_product_data}
                    prod_response = self.callMagentoApi(
                        baseUrl=url,
                        url="/V1/odoomagentoconnect/products",
                        method='post',
                        token=token,
                        data=product_data
                    )
                exup_product_obj.need_sync = 'No'
                return {'status': 1, 'ecomm_id': temp_obj.id}