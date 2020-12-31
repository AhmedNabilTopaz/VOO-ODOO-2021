# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models


class MagentoWebsite(models.Model):
    _name = "magento.website"
    _description = "Magento Website"

    name = fields.Char(string='Website Name', size=64, required=True)
    website_id = fields.Integer(string='Magento Webiste Id', readonly=True)
    instance_id = fields.Many2one(
        'connector.instance', string='Magento Instance')
    ecommerce_channel = fields.Selection(
        related="instance_id.ecomm_type", 
        string="eCommerce Channel", store=True)
    code = fields.Char(string='Code', size=64, required=True)
    default_group_id = fields.Integer(string='Default Store', readonly=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)

    @api.model
    def _get_website(self, url, token):
        website_id = False
        instance_id = self._context.get('instance_id')
        magento_websites = []
        stores_response = self.env['connector.snippet'].callMagentoApi(
            baseUrl=url,
            url='/V1/store/websites',
            method='get',
            token=token
        )
        if stores_response :
            magento_websites = stores_response
        for magento_website in magento_websites:
            if not magento_website.get('id'):
                continue
            website_objs = self.search(
                [('website_id', '=', magento_website['id']), ('instance_id', '=', instance_id)])
            if website_objs:
                website_obj = website_objs
            else:
                website_dict = {
                    'name': magento_website['name'],
                    'code': magento_website['code'],
                    'instance_id': instance_id,
                    'website_id': magento_website['id'],
                    'default_group_id': magento_website['default_group_id']
                }
                website_obj = self.create(website_dict)
            website_id = website_obj.id
        return website_id
