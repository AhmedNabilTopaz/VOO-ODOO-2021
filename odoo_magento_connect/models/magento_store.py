# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


from odoo import api, fields, models


class MagentoStore(models.Model):
    _name = "magento.store"
    _description = "Magento Store"

    name = fields.Char(string='Store Name', size=64, required=True)
    group_id = fields.Integer(string='Magento Store Id', readonly=True)
    instance_id = fields.Many2one(
        'connector.instance', string='Magento Instance')
    ecommerce_channel = fields.Selection(
        related="instance_id.ecomm_type", 
        string="eCommerce Channel", store=True)
    root_category_id = fields.Integer(string='Root Category Id', readonly=True)
    default_store_id = fields.Integer(string='Default Store Id')
    website_id = fields.Many2one('magento.website', string='Website')
    create_date = fields.Datetime(string='Created Date', readonly=True)

    @api.model
    def _get_store_group(self, url, token):
        group_id = False
        instance_id = self._context.get('instance_id')
        magento_stores = []
        stores_response = self.env['connector.snippet'].callMagentoApi(
            baseUrl=url,
            url='/V1/store/storeGroups',
            method='get',
            token=token
        )
        if stores_response :
            magento_stores = stores_response
            self.env['magento.website']._get_website(url, token)
        for magento_store in magento_stores:
            if not magento_store.get('id'):
                continue
            group_objs = self.search(
                [('group_id', '=', magento_store['id']), ('instance_id', '=', instance_id)])
            if group_objs:
                group_obj = group_objs[0]
            else:
                website_objs = self.env['magento.website'].search(
                    [('website_id', '=', magento_store['website_id']), ('instance_id', '=', instance_id)])
                if website_objs:
                    website_id = website_objs[0].id
                group_dict = {
                    'name': magento_store['name'],
                    'website_id': website_id,
                    'group_id': magento_store['id'],
                    'instance_id': instance_id,
                    'root_category_id': magento_store['root_category_id'],
                    'default_store_id': magento_store['default_store_id'],
                }
                group_obj = self.create(group_dict)
            group_id = group_obj.id
        return group_id
