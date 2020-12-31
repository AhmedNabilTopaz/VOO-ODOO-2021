# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import logging
import json
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta

from babel.dates import format_date, format_datetime

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


Item_Type = [
    ('product', 'Product'),
    ('order', 'Order'),
    ('attribute', 'Attribute'),
    ('category', 'Category'),
    ('partner', 'Partner'),
]

modelName = {
    'product': [
        1,
        'product.template',
        'connector.template.mapping',
        'name',
        'connector_template_mapping'],
    'category': [
        1,
        'product.category',
        'connector.category.mapping',
        'name',
        'connector_category_mapping'],
    'order': [
        2,
        'sale.order',
        'connector.order.mapping',
        'odoo_order_id',
        'connector_order_mapping'],
    'partner': [
        0,
        'res.partner',
        'connector.partner.mapping',
        '',
        'connector_partner_mapping'],
    'attribute': [
        0,
        'product.attribute',
        'connector.attribute.mapping',
        'name',
        'connector_attribute_mapping'],
}

fieldName = {
    'product': [
        'count_need_sync_product',
        'count_no_sync_product',
        'product.product_template_form_view'],
    'category': [
        'count_need_sync_category',
        'count_no_sync_category',
        'product.product_category_form_view'],
    'order': [
        'count_need_invoice',
        'count_need_delivery',
        'sale.view_order_form'],
    'partner': [
        '',
        '',
        'base.view_partner_form'],
    'attribute': [
        '',
        'count_no_sync_attribute',
        'product.product_attribute_view_form'],
}


class ConnectorDashboard(models.Model):
    _name = "connector.dashboard"
    _description = "Connector Dashboard"

    def _kanban_dashboard_graph(self):
        for record in self:
            record.kanban_dashboard_graph = json.dumps(
                record.get_bar_graph_datas(record.item_name))

    name = fields.Char(string="Dashboard Item")
    instance_id = fields.Many2one(
        'connector.instance', 'Ecomm Instance', ondelete='cascade')
    ecommerce_channel = fields.Selection(
        related="instance_id.ecomm_type", 
        string="eCommerce Channel", store=True)
    active = fields.Boolean(related="instance_id.active")
    item_name = fields.Selection(
        Item_Type, string="Dashboard Item Name")
    color = fields.Integer(string='Color Index')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    count_mapped_records = fields.Integer(compute='_compute_record_count')
    count_need_sync_product = fields.Integer()
    count_no_sync_product = fields.Integer()
    count_need_sync_category = fields.Integer()
    count_no_sync_category = fields.Integer()
    count_need_invoice = fields.Integer()
    count_need_delivery = fields.Integer()
    count_invoiced_records = fields.Integer()
    count_delivered_records = fields.Integer()
    count_no_sync_attribute = fields.Integer()

    def _count_map(self):
        for record in self:
            record['count_mapped_records'] = []

    @api.model
    def get_connection_info(self):
        configModel = self.env['connector.instance']
        success = False
        defId = False
        activeConObjs = configModel.search([('active', '=', True)])
        inactiveConObjs = configModel.search([('active', '=', False)])
        if activeConObjs:
            defConnection = activeConObjs[0]
            defId = defConnection.id
            if defConnection.connection_status:
                success = True
        totalConnections = activeConObjs.ids + inactiveConObjs.ids
        res = {
            'totalcon' : len(totalConnections),
            'total_ids' : totalConnections,
            'active_ids' : activeConObjs.ids,
            'inactive_ids' : inactiveConObjs.ids,
            'active' : len(activeConObjs.ids),
            'inactive' : len(inactiveConObjs.ids),
            'def_id' : defId,
            'success' : success
        }
        return res

    def open_configuration(self):
        self.ensure_one()
        instanceId = self.get_instance()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configure Connection',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'connector.instance',
            'res_id': instanceId,
            'target': 'current',
            'domain': '[]',
        }

    @api.model
    def _create_dashboard(self, instanceObj):
        for itemName in Item_Type:
            vals = {
                'name' : itemName[1],
                'instance_id' : instanceObj.id,
                'item_name' : itemName[0],
            }
            self.create(vals)
        return True

    
    def get_instance(self):
        instanceId = False
        connector_instance = self.env['connector.instance']
        check_dashboard = connector_instance.sudo().search([('active','=',True),('current_instance','=',True)])
        if check_dashboard and len(check_dashboard)==1:
            instanceId = check_dashboard.id
        if not instanceId:
            check_dashboard = connector_instance.sudo().search([('active','=',True)],limit=1)
            if check_dashboard and len(check_dashboard)==1:
                check_dashboard.current_instance = True
                instanceId = check_dashboard.id
        return instanceId

    def _compute_record_count(self):
        for single_record in self:
            instanceId = self.instance_id.id
            name = self[0].item_name
            needOne = fieldName[name][0]
            needTwo = fieldName[name][1]
            model = modelName[name][1]
            mappedModel = modelName[name][2]
            mappedfieldName = modelName[name][3]
            action = modelName[name][0]
            if action == 1:
                totalOne = self._get_need_sync_record(mappedModel, instanceId)
                totalTwo = self._get_no_sync_record(
                    model, mappedModel, mappedfieldName, instanceId)
                self[0][needOne] = totalOne
                self[0][needTwo] = totalTwo
            elif action == 2:
                totalInvc, totalNeedInv, totalDlvr, totlaNeedDlvr = self._get_processed_unprocessed_records(
                    instanceId)
                self[0][needOne] = len(totalNeedInv)
                self[0][needTwo] = len(totlaNeedDlvr)
                self[0].count_invoiced_records = len(totalInvc)
                self[0].count_delivered_records = len(totalDlvr)
            elif mappedfieldName:
                self[0][needTwo] = self._get_no_sync_record(
                    model, mappedModel, mappedfieldName, instanceId)
            
            self[0].count_mapped_records = self._get_mapped_records(
                mappedModel, instanceId)

    @api.model
    def _get_mapped_records(self, mappedModel, instanceId):
        return self.env[mappedModel].search_count(
            [('instance_id', '=', instanceId)])

    @api.model
    def _get_need_so_action_record(self, instanceId, needAction):
        recordMapObjs = self.env['connector.order.mapping'].search(
            [('instance_id', '=', instanceId)])
        saleOrderObjs = recordMapObjs.mapped('odoo_order_id')
        idList = []
        for orderObj in saleOrderObjs.filtered(
                lambda obj: obj.state != 'cancel'):
            if needAction == 'delivery':
                if not orderObj.is_shipped:
                    idList.append(orderObj.id)
            if needAction == 'invoice':
                if not orderObj.is_invoiced:
                    idList.append(orderObj.id)

        return idList

    @api.model
    def _get_process_order_record(self, instanceId, doneAction):
        recordMapObjs = self.env['connector.order.mapping'].search(
            [('instance_id', '=', instanceId)])
        recList = []
        for orderObj in recordMapObjs:
            if doneAction == 'invoice' and orderObj.is_invoiced:
                recList.append(orderObj.odoo_order_id.id)
            if doneAction == 'delivery' and orderObj.is_shipped:
                recList.append(orderObj.odoo_order_id.id)
        return recList

    @api.model
    def _get_processed_unprocessed_records(self, instanceId):
        recordMapObjs = self.env['connector.order.mapping'].search(
            [('instance_id', '=', instanceId)])
        saleOrderIds = recordMapObjs.mapped('odoo_order_id').ids
        filterDate = self.get_order_filter_date()
        domain = [
            ('id', 'in', saleOrderIds),
            ('state', '!=', 'cancel'),
            ('date_order', '>=', filterDate)]
        saleOrderObjs = self.env['sale.order'].search(domain)
        totalInvc, totalNeedInv, totalDlvr, totlaNeedDlvr = [], [], [], []
        for orderObj in saleOrderObjs:
            if orderObj.is_invoiced:
                totalInvc.append(orderObj.id)
            else:
                totalNeedInv.append(orderObj.id)
            if orderObj.is_shipped:
                totalDlvr.append(orderObj.id)
            else:
                totlaNeedDlvr.append(orderObj.id)
        return [totalInvc, totalNeedInv, totalDlvr, totlaNeedDlvr]


    @api.model
    def get_order_filter_date(self):
        crntDate = datetime.datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        dateFormat = '%Y-%m-%d %H:%M:%S'
        crntDate = datetime.datetime.strptime(crntDate, dateFormat)
        filterDate = crntDate + relativedelta(days=-30)
        return filterDate

    def get_action_prosess_records(self):
        self.ensure_one()
        instanceId = self.get_instance()
        doneAction = self._context.get('action')
        doneActionIds = self._get_process_order_record(instanceId, doneAction)
        return {
            'name': ('Records'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'domain': [('id', 'in', doneActionIds)],
            'target': 'current',
        }

    def action_open_order_need(self):
        self.ensure_one()
        instanceId = self.get_instance()
        needAction = self._context.get('action')
        neddActionIds = self._get_need_so_action_record(instanceId, needAction)
        return {
            'name': ('Record'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'domain': [('id', 'in', neddActionIds)],
            'target': 'current',
        }

    @api.model
    def _get_need_sync_record(self, mappedModel, instanceId):
        domain = [('need_sync', '=', "Yes"), ('instance_id', '=', instanceId)]
        needSyncCount = self.env[mappedModel].search_count(domain)
        return needSyncCount

    @api.model
    def _get_no_sync_record(
            self,
            model,
            mappedModel,
            mappedfieldName,
            instanceId):
        if model == "product.template":
            domin = [('type', '!=', 'service')]
        else:
            domin = []
        allRecordIds = self.env[model].search(domin).ids
        allSyncedObjs = self.env[mappedModel].search(
            [('instance_id', '=', instanceId)])
        allSynedRecordIds = allSyncedObjs.mapped(mappedfieldName).ids
        return len(set(allRecordIds) - set(allSynedRecordIds))

    def get_action_mapped_records(self):
        self.ensure_one()
        resModel = self._context.get('map_model')
        recordIds = self.env[resModel].search(
            [('instance_id', '=', self.get_instance())]).ids
        return {
            'name': ('Records'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': resModel,
            'view_id': False,
            'domain': [('id', 'in', recordIds)],
            'target': 'current',
        }

    def open_action(self):
        self.ensure_one()
        itemType = self.item_name
        ctx = dict(
            map_model=modelName[itemType][2]
        )
        res = self.with_context(ctx).get_action_mapped_records()
        return res

    def show_report(self):
        self.ensure_one()
        ctx = dict(self._context or {})
        repType = ctx.get('r_type')
        itemType = self.item_name
        if itemType == "partner":
            itemType = "customer"
        if repType == 'success':
            status = 'yes'
        else:
            status = 'no'
        resModel = "connector.sync.history"
        domain = [('status', '=', status), ('action_on', '=', itemType)]
        itemHistory = self.env[resModel].search(domain).ids
        return {
            'name': ('Reports'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': resModel,
            'view_id': False,
            'domain': [('id', 'in', itemHistory)],
            'target': 'current',
        }

    def open_view_rec(self):
        self.ensure_one()
        ctx = dict(self._context or {})
        instanceId = self.get_instance()
        resModel = ctx.get('res_model')
        rType = ctx.get('rec_type')
        domain = [('instance_id', '=', instanceId)]
        if rType == 'config':
            domain += [('is_variants', '=', True)]
        elif rType == 'simple':
            domain += [('is_variants', '=', False)]
        elif rType == 'partner':
            domain += [('ecomm_address_id', '=', 'customer')]
        elif rType == 'address':
            domain += [('ecomm_address_id', '!=', 'customer')]
        recIds = self.env[resModel].search(domain).ids
        return {
            'name': ('Records'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': resModel,
            'view_id': False,
            'domain': [('id', 'in', recIds)],
            'target': 'current',
        }

    def open_order_view_rec(self):
        self.ensure_one()
        ctx = dict(self._context or {})
        instanceId = self.get_instance()
        resModel = ctx.get('res_model')
        rType = ctx.get('rec_type')
        domain = [('instance_id', '=', instanceId)]
        orderObjs = self.env[resModel].search(domain)
        recIds = []
        for orderObj in orderObjs:
            if orderObj.order_status == rType:
                recIds.append(orderObj.id)

        return {
            'name': ('Records'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': resModel,
            'view_id': False,
            'domain': [('id', 'in', recIds)],
            'target': 'current',
        }

    def action_open_update_records(self):
        self.ensure_one()
        resModel = self._context.get('map_model')
        domain = [('instance_id', '=', self.get_instance()),
                  ('need_sync', '=', 'Yes')]
        recordIds = self.env[resModel].search(domain).ids
        return {
            'name': ('Record'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': resModel,
            'view_id': False,
            'domain': [('id', 'in', recordIds)],
            'target': 'current',
        }

    def create_new_rec(self):
        self.ensure_one()
        ctx = dict(self._context or {})
        itemType = self.item_name
        resModel = modelName[itemType][1]
        envRefId = fieldName[itemType][2]
        viewId = self.env.ref(envRefId).id
        return {
            'name': _('Create'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': resModel,
            'view_id': viewId,
            'context': ctx,
        }

    def action_open_export_records(self):
        self.ensure_one()
        mapModel = self._context.get('map_model')
        coreModel = self._context.get('core_model')
        fieldName = self._context.get('field_name')
        domain = []
        mappedObj = self.env[mapModel].search(
            [('instance_id', '=', self.get_instance())])
        mapObjIds = mappedObj.mapped(fieldName).ids
        if coreModel == 'product.template':
            domain += [('type', '!=', 'service')]
        recordIds = self.env[coreModel].search(domain).ids
        notMapIds = list(set(recordIds) - set(mapObjIds))

        return {
            'name': ('Record'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': coreModel,
            'view_id': False,
            'domain': [('id', 'in', notMapIds)],
            'target': 'current',
        }

    def get_bar_graph_datas(self, itemName):
        self.ensure_one()
        itemType = self.item_name
        if itemType in ['order', 'partner']:
            fecthDate = 'create_date'
        else:
            fecthDate = 'write_date'
        moduleDB = modelName[itemType][4]
        data = []
        today = fields.Date.context_today(self)
        data.append({'label': _('Past'), 'value': 0.0})
        day_of_week = int(
            format_datetime(
                today,
                'e',
                locale=self._context.get(
                    'lang',
                    'en_US')))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        for i in range(-1, 1):
            if i == 0:
                label = _('This Week')
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' + str(end_week.day) + ' ' + format_date(
                        end_week, 'MMM', locale=self._context.get('lang', 'en_US'))
                else:
                    label = format_date(start_week, 'd MMM', locale=self._context.get('lang', 'en_US')) \
                        + '-' \
                        + format_date(end_week, 'd MMM', locale=self._context.get('lang', 'en_US'))
            data.append({'label': label, 'value': 0.0})

        # Build SQL query to find amount aggregated by week
        select_sql_clause = """SELECT COUNT(*) as total FROM """ + \
            moduleDB + """ where instance_id = %(instance_id)s """
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        for i in range(0, 3):
            if i == 0:
                query += "(" + select_sql_clause + " and " + \
                    fecthDate + " < '" + start_date.strftime(DF) + "')"
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + " and " + fecthDate + " >= '" + start_date.strftime(
                    DF) + "' and " + fecthDate + " < '" + next_date.strftime(DF) + "')"
                start_date = next_date

        self.env.cr.execute(query, {'instance_id': self.get_instance()})
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            total = str(query_results[index].get('total'))
            total = total.split('L')
            if int(total[0]) > 0:
                data[index]['value'] = total[0]

        color = '#7c7bad'
        graphData = [{'values': data, 'area': True, 'title': '', 'key': itemName.title(), 'color': color}]
        return graphData



    @api.model
    def dashboard_extend_data(self):
        pass

    @api.model
    def open_bulk_synchronization(self):
        viewId = self.env.ref(
            'bridge_skeleton.connector_synchronization_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ecomm Synchronization'),
            'res_model': 'connector.snippet',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[viewId, 'form']],
        }

    @api.model
    def create_new_connection(self):
        action = self.env.ref(
            'bridge_skeleton.connector_instance_tree_action').read()[0]
        action['views'] = [
            (self.env.ref('bridge_skeleton.connector_instance_form').id, 'form')]
        return action

    @api.model
    def open_mob_success_connection(self):
        instance_id = self.get_instance()
        return self.open_connection_form(instance_id)
        # return self.open_connection_tree(connInfo[1], 'search_default_success')

    @api.model
    def open_mob_error_connection(self):
        instance_id = self.get_instance()
        return self.open_connection_form(instance_id)
        # return self.open_connection_tree(connInfo[1], 'search_default_error')

    @api.model
    def get_total_connection(self):
        totalActiveConn = self.env['connector.instance'].search(
            [('active', '=', True)])
        if totalActiveConn and len(totalActiveConn) == 1:
            return [1, totalActiveConn]
        return [2, totalActiveConn]

    @api.model
    def open_connection_form(self, connObj):
        action = self.env.ref(
            'bridge_skeleton.connector_instance_tree_action').read()[0]
        action['views'] = [
            (self.env.ref('bridge_skeleton.connector_instance_form').id, 'form')]
        action['res_id'] = connObj
        return action
