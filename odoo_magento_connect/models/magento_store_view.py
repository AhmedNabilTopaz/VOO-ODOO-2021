# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


from odoo import api, fields, models


class MagentoStoreView(models.Model):
    _name = "magento.store.view"
    _description = "Magento Store View"

    name = fields.Char(string='Store View Name', size=64, required=True)
    code = fields.Char(string='Code', size=64, required=True)
    view_id = fields.Integer(string='Magento Store View Id', readonly=True)
    instance_id = fields.Many2one(
        'connector.instance', string='Magento Instance')
    ecommerce_channel = fields.Selection(
        related="instance_id.ecomm_type", 
        string="eCommerce Channel", store=True)
    group_id = fields.Many2one('magento.store', string='Store Id')
    create_date = fields.Datetime(string='Created Date', readonly=True)

    @api.depends('name', 'group_id')
    def name_get(self):
        result = []
        for record in self:
            name = record.name + \
                "\n(%s)" % (record.group_id.name) + \
                "\n(%s)" % (record.group_id.website_id.name)
            result.append((record.id, name))
        return result

    @api.model
    def _get_store_view(self, url, token):
        store_view_id = False
        instance_id = self._context.get('instance_id')
        magento_store_views = []
        store_views_response = self.env['connector.snippet'].callMagentoApi(
            baseUrl=url,
            url='/V1/store/storeViews',
            method='get',
            token=token
        )
        if store_views_response :
            magento_store_views = store_views_response
            self.env['magento.store']._get_store_group(url, token)
        for magento_store_view in magento_store_views:
            if not magento_store_view.get('id'):
                continue
            store_view_objs = self.search(
                [('view_id', '=', magento_store_view['id']), ('instance_id', '=', instance_id)])
            if store_view_objs:
                store_view_obj = store_view_objs[0]
            else:
                group_obj = self.env['magento.store'].search(
                    [('group_id', '=', magento_store_view['store_group_id']), ('instance_id', '=', instance_id)])
                if group_obj:
                    group_id = group_obj[0].id
                view_dict = {
                    'name': magento_store_view['name'],
                    'code': magento_store_view['code'],
                    'view_id': magento_store_view['id'],
                    'group_id': group_id,
                    'instance_id': instance_id,
                }
                store_view_obj = self.create(view_dict)
            store_view_id = store_view_obj.id
        return store_view_id
