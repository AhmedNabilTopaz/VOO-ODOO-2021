# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import http,fields
from odoo.http import request
from odoo.osv import expression


class OnboardingController(http.Controller):

    # @http.route('/bridge_skeleton/bridge_skeleton_dashboard_onboarding', auth='user', type='json')
    # def connector_dashboard_onboarding(self):
    #     connectInfo = request.env['connector.dashboard'].get_connection_info()
    #     return {
    #         'html': request.env.ref('bridge_skeleton.bridge_skeleton_dashboard_onboarding_panel').render({
    #             'connrecs': connectInfo})
    #     }


    @http.route('/bridge_skeleton/infos', type='json', auth='user')
    def infos(self):
        infos = {}
        instance_id = request.env['connector.dashboard'].sudo().get_instance() 
        if instance_id:
            instance_id = request.env['connector.instance'].sudo().browse(instance_id)
            extensions = request.env['connector.snippet'].sudo()._get_ecomm_extensions()
            current_ecomm = [i for i in extensions if i[0]== instance_id.ecomm_type]
            infos.update({
            'instance_detail': (instance_id.id, instance_id.instance_name),
            'current_ecomm':current_ecomm,
            'active':True,
            'extensions':extensions})
            href_data = request.env['wk.skeleton'].get_ecomm_href(current_ecomm[0][0])
            if href_data:
                if href_data.get('user_guide'):
                    infos['user_guide'] = href_data['user_guide']
                if href_data.get('rate_review'):
                    infos['rate_review'] = href_data['rate_review']
                if href_data.get('extension'):
                    infos['extension'] = href_data['extension']
                if href_data.get('name'):
                    infos['bridge_name'] = href_data['name']
                if href_data.get('short_form'):
                    infos['bridge_short_form'] = href_data['short_form']
                if href_data.get('img_link'):
                    infos['img_link'] = href_data['img_link']
            if instance_id.connection_status:
                infos['status'] = True
        else:
            infos.update({
            'instance_detail': ('', ''),
            'current_ecomm':[('','')],
            })
        return infos


    @http.route('/bridge_skeleton/skeleton_instance_set', type='json', auth='user')
    def skeleton_instance_set(self, instance_id=None):
        check_dashboard = request.env['connector.instance'].sudo().search([('current_instance','=',True)])
        check_dashboard.sudo().write({'current_instance':False})
        if instance_id:
            instance_search = request.env['connector.instance'].sudo().browse(int(instance_id))
            if instance_search and len(instance_search)==1:
                instance_search.sudo().current_instance = True
        return True
    
    @http.route('/bridge_skeleton/get_instance_id', type='json', auth='user')
    def get_instance_id(self):
        instance_id = request.env['connector.dashboard'].sudo().get_instance()
        if instance_id:
            return instance_id
        return False
    
    @http.route('/bridge_skeleton/skeleton_channel_set', type='json', auth='user')
    def skeleton_channel_set(self, channel_id = False):
        instance_ids =  self.get_instances(channel_id)
        if instance_ids:
            check_dashboard = request.env['connector.instance'].sudo().search([('current_instance','=',True)])
            check_dashboard.sudo().write({'current_instance':False})
            instance_ids[0].sudo().write({'current_instance':True})
            return instance_ids[0].id
        else:
            instance_id = request.env['connector.dashboard'].sudo().get_instance()
            if instance_id:
                return instance_id
        return False
    
    def get_instances(self,channel_id):
        if channel_id:
            instance_ids = request.env['connector.instance'].sudo().search([('ecomm_type','=',channel_id)])
            return instance_ids
        return False



