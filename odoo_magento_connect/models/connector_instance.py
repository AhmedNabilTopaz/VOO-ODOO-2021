# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import json
import re

import requests
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError

XMLRPC_API = '/integration/admin/token'

class ConnectorInstance(models.Model):
    _inherit = "connector.instance"

    store_id = fields.Many2one(
        'magento.store.view', string='Default Magento Store')
    group_id = fields.Many2one(
        related="store_id.group_id",
        string="Default Store",
        readonly=True,
        store=True)
    website_id = fields.Many2one(
        related="group_id.website_id",
        string="Default Magento Website",
        readonly=True)

    def test_magento_connection(self):
        token = 0
        connection_status = False
        status = 'Magento Connection Un-successful'
        text = 'Test connection Un-successful please check the magento login credentials !!!'
        # check_mapping = self.correct_mapping
        token = self.create_magento_connection()
        if token.get('token', ''):
            self.token = str(token.get('token', ''))
            self.set_default_magento_website(
                self.name, self.token)
            text = str(token.get('message', ''))
            status = "Congratulation, It's Successfully Connected with Magento."
            connection_status = True
        else:
            status = str(token.get('message', ''))
        self.status = status
        res_model = 'message.wizard'
        partial = self.env['message.wizard'].create({'text': text})
        view_id = False
        if not self.store_id and connection_status:
            partial = self.env['magento.wizard'].create(
                {'magento_store_view': self.store_id.id})
            view_id = self.env.ref(
                'odoo_magento_connect.id_magento_wizard_form').id
            res_model = 'magento.wizard'
        # if check_mapping:
        #     self.correct_instance_mapping()
        ctx = dict(self._context or {})
        ctx['text'] = text
        ctx['instance_id'] = self.id
        self.connection_status = connection_status
        return {'name': ("Odoo Magento Bridge"),
                'view_mode': 'form',
                'res_model': res_model,
                'view_id': view_id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'context': ctx,
                'target': 'new',
                }

    def _create_magento_connection(self):
        """ create a connection between Odoo and magento 
                returns: False or list"""
        instance_id = self._context.get('instance_id', False)
        token, message, instance_obj = '', '', False
        resp = {'status':False, 'message': message}
        if instance_id:
            instance_obj = self.browse(instance_id)
        else:
            active_connections = self.search([('active', '=', True), ('ecomm_type', '=', 'magento')])
            if not active_connections:
                resp['message'] = _('Error!\nPlease create the configuration part for Magento connection!!!')
            elif len(active_connections) > 1:
                resp['message'] = _('Error!\nSorry, only one Active Configuration setting is allowed.')
            else:
                instance_obj = active_connections[0]
        if instance_obj:
            token_generation = instance_obj.create_magento_connection()
            token = token_generation.get('token', '')
            if token:
                instance_obj.token = token
                resp = {
                    'url':instance_obj.name,
                    'token':token,
                    'instance_id':instance_obj.id,
                    'status':True,
                    'message': token_generation.get('message', '')
                }
        return resp

    def create_magento_connection(self, vals={}):
        text, token = '', ''
        url = self.name + "/index.php/rest/V1" + XMLRPC_API
        user, pwd = self.user, self.pwd
        if vals:
            if vals.get('name'):
                url = vals['name'] + "/index.php/rest/V1" + XMLRPC_API
            if vals.get('user'):
                user = vals['user']
            if vals.get('pwd'):
                pwd = vals['pwd']
        try:
            response_api = requests.post(
                url,
                data=json.dumps({"username": user, "password": pwd}),
                headers={'Content-Type': 'application/json', 'User-Agent': request.httprequest.environ.get('HTTP_USER_AGENT', '')},
                verify=False
            )
            response = json.loads(response_api.text)
            if response_api.ok :
                token = "Bearer " + response
                text = 'Test Connection with magento is successful, now you can proceed with synchronization.'
            else :
                text = ('Magento Connection Error: %s') % response.get('message')
        except Exception as e:
            text = ('Error!\nMagento Connection Error: %s') % e
        return {'token':token, 'message':text}

    def set_default_magento_website(self, url, token):
        for obj in self:
            store_id = obj.store_id
            ctx = dict(self._context or {})
            ctx['instance_id'] = obj.id
            if not store_id:
                store_info = self.with_context(
                    ctx)._fetch_magento_store(url, token)
                if not store_info:
                    raise UserError(
                        _('Error!\nMagento Default Website Not Found!!!'))
        return True

    def _fetch_magento_store(self, url, token):
        store_info = {}
        store_obj = self.env['magento.store.view']._get_store_view(url, token)
        store_info['store_id'] = store_obj
        return store_info

    @api.model
    def fetch_connection_info(self, vals):
        """
                Called by Xmlrpc from Magento
        """
        if vals.get('magento_url'):
            active_connections = self.search([('active', '=', True)])
            is_multi_mob_installed = self.env['ir.module.module'].sudo().search(
                [('name', 'in', ['odoo_magento_multi_instance', 'mob_hybrid_multi_instance']), ("state", "=", "installed")])
            if is_multi_mob_installed:
                magento_url = re.sub(r'^https?:\/\/', '', vals.get('magento_url'))
                magento_url = re.split('index.php', magento_url)[0]
                for connection_obj in active_connections:
                    act = connection_obj.name
                    act = re.sub(r'^https?:\/\/', '', act)
                    if magento_url == act or magento_url[:-1] == act:
                        return connection_obj.read(
                            ['language', 'category', 'warehouse_id'])[0]
            else:
                for connection_obj in active_connections:
                    return connection_obj.read(
                        ['language', 'category', 'warehouse_id'])[0]
        return False