# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models

class ConnectorSnippet(models.TransientModel):
    _name = "connector.snippet"
    _description = "Connector Snippet"

    @api.model
    def _get_ecomm_extensions(self):
        return []

    def open_configuration(self):
        connection_id = False
        active_conn = self.env['connector.instance'].search(
            [('active', '=', True)], limit=1)
        if active_conn:
            connection_id = active_conn.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configure Connection',
            'view_mode': 'form',
            'res_model': 'connector.instance',
            'res_id': connection_id,
            'domain': '[]',
        }

    def export_attributes_and_their_values(self):
        display_message = "<h4 class='text-danger'><i class='fa fa-exclamation-triangle'></i> Error in ecommerce connection kindly check connection</h4>"
        connection = self.env['connector.instance']._create_connection()
        if type(connection) is dict and connection.get('status', 'False'):
            display_message = self.sync_ecomm_attribute(connection)
        return self.env['message.wizard'].genrated_message(display_message)

    def sync_operations(self, model, mapping_model, domain, oprmodel):
        display_message = "<h4 class='text-danger'><i class='fa fa-exclamation-triangle'></i> Error in ecommerce connection kindly check connection</h4>"
        connection = self.env['connector.instance']._create_connection()
        if type(connection) is dict and connection.get('status', 'False'):
            ctx = dict(self._context or {})
            sync_opr = ctx.get('sync_opr')
            instance_id = ctx.get('instance_id')
            channel = ctx.get('ecomm_channel', False)
            record_objs = self.env[model].browse(ctx.get('active_ids', [])) if ctx.get('active_model') == model else self.env[model].search(domain)
            if record_objs:
                exup_record_objs = self.get_map_updt_objs(record_objs, instance_id, sync_opr, mapping_model)
                if exup_record_objs:
                    if hasattr(self, 'sync_ecomm_%s' % oprmodel):
                        display_message = getattr(self, 'sync_ecomm_%s' % oprmodel)(exup_record_objs, channel, instance_id, sync_opr, connection)
                else:
                    display_message = 'Information!\nListed {}(s) has been already exported/updated.'.format(oprmodel)
            else:
                display_message = 'Information!\nNo new {}(s) found to be Sync.'.format(oprmodel)
        return self.env['message.wizard'].genrated_message(display_message)

    @api.model
    def get_map_updt_objs(self, record_objs, instance_id, sync_opr, model):
        mapped_objs = self.env[model].search([('instance_id', '=', instance_id)])
        if sync_opr == 'export':
            return list(set(record_objs) - set(mapped_objs.mapped('name')))
        elif sync_opr == 'update':
            return mapped_objs.filtered(
                lambda obj: obj.need_sync == 'Yes' and
                int(obj.name.id) in record_objs.ids)
        return []

    def create_odoo_connector_mapping(self, model, ecomm_id, odoo_id, instance_id, **kwargs):
        mapping_data = {
            'name' : odoo_id,
            'odoo_id' : odoo_id,
            'ecomm_id' : ecomm_id,
            'created_by' : 'odoo',
            'instance_id' : instance_id,
        }
        channel = kwargs.pop('channel', False)
        if not channel and instance_id:
            channel = self.env['connector.instance'].browse(instance_id).ecomm_type
        mapping_data.update(kwargs)
        if channel:
            if hasattr(self, 'create_%s_connector_odoo_mapping' % channel):
                mapping_data = getattr(self, 'create_%s_connector_odoo_mapping' % channel)(mapping_data, model)
        self.env[model].create(mapping_data)
        return True

    def create_ecomm_connector_mapping(self, model, channel, data, connection):
        if hasattr(self, 'create_%s_connector_mapping' % channel):
            getattr(self, 'create_%s_connector_mapping' % channel)(model, data, connection)
        return True

    def update_ecomm_connector_mapping(self, model, channel, data, connection):
        if hasattr(self, 'update_%s_connector_mapping' % channel):
            getattr(self, 'update_%s_connector_mapping' % channel)(model, data, connection)
        return True

    def update_odoo_mapping(self, model, mapping_ids, data):
        return self.env[model].browse(mapping_ids).write(data) if mapping_ids else False

    @api.model
    def update_quantity(self, data):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param data: List of product_id and new_quantity
        @return: True
        """
        warehouse_data = data.get('warehouse_data', False)
        if warehouse_data:
            for warehouse in warehouse_data:
                location_objs = self.env['connector.warehouse.mapping'].search(
                    [('source_code', '=', warehouse['warehouse_id'])], limit=1)
                if location_objs:
                    self.env['stock.quant'].with_context(inventory_mode=True).create({
                                'product_id': data.get('product_id'),
                                'location_id': location_objs.name.lot_stock_id.id,
                                'inventory_quantity': int(warehouse.get('qty', 0)),
                    })
        else:
            ctx = dict(self._context or {})
            if 'instance_id' in ctx:
                connection_obj = self.env['connector.instance'].browse(ctx.get('instance_id'))
                location_objs = connection_obj.warehouse_id if connection_obj.active else self.env['stock.warehouse'].search([], limit=1)
                if location_objs:
                    self.env['stock.quant'].with_context(inventory_mode=True).create({
                                'product_id': data.get('product_id'),
                                'location_id': location_objs.lot_stock_id.id,
                                'inventory_quantity': int(data.get('new_quantity', 0)),
                    })
                    return True
        return False

    @api.model
    def _get_journal_code(self, name, sep=' '):
        name_sep_list = []
        for namp_split in name.split(sep):
            if namp_split:
                name_seprtd = namp_split.title()[0]
                if name_seprtd.isalnum():
                    name_sep_list.append(name_seprtd)
        code = ''.join(name_sep_list)
        code = code[0:3]
        journal_model = self.env['account.journal']
        exist_obj = journal_model.search([('code', '=', code)])
        if exist_obj:
            for i in range(1, 200):
                exist_obj = journal_model.search(
                    [('code', '=', code + str(i))])
                if not exist_obj:
                    return (code + str(i))[-5:]
        return code

    @api.model
    def create_payment_method(self, data):
        """create Journal by any webservice like xmlrpc.
        @param name: journal name.
        @return: payment_id
        """
        payment_id = 0
        status = True
        status_message = "Payment method created successfully."
        try:
            journal_model = self.env['account.journal']
            res = journal_model.search(
                [('type', '=', 'cash')], limit=1)
            if res:
                data['default_credit_account_id'] = res[
                    0].default_credit_account_id.id
                data['default_debit_account_id'] = res[
                    0].default_debit_account_id.id
                data['code'] = self._get_journal_code(data.get('name'), ' ')
                paymentObj = journal_model.create(data)
                payment_id = paymentObj.id
            else:
                status_message = 'No cash journal exists!!'
                status = False
        except Exception as e:
            status = False
            status_message = "Exception in creating payment method . Reason: %s" % str(e)
        finally:
            return {
                'status_message': status_message,
                'status': status,
                'odoo_id' : payment_id,
            }

    # code for update an inventry of a product......

    @api.model
    def create_pricelist(self, data):
        """create and search pricelist by any webservice like xmlrpc.
        @param code: currency code.
        @return: pricelist_id
        """
        currencyObj = self.env['res.currency'].search(
            [('name', '=', data['code'])], limit=1)
        priceListModel = self.env['product.pricelist']
        if currencyObj:
            pricelistObj = priceListModel.search(
                [('currency_id', '=', currencyObj.id)], limit=1)
            if not pricelistObj:
                pricelistDict = {
                    'name' : 'Mage_' + data['code'],
                    'active' : True,
                    'currency_id' : currencyObj.id
                }
                pricelistObj = priceListModel.create(pricelistDict)
                return pricelistObj.id
            else:
                return pricelistObj.id
        return 0

    def manual_connector_order_operation(self, opr, ecomm, sale_order, opr_obj=False):
        text, status, session, mage_shipment, response = '', 'no', False, False, {}
        order_map_obj = self.env['connector.order.mapping'].search(
            [('odoo_order_id', '=', sale_order.id)], limit=1)
        if order_map_obj:
            increment_id = order_map_obj.name
            ecomm_order_id = order_map_obj.ecommerce_order_id or 0
            connection_obj = order_map_obj.instance_id
            instance_id = connection_obj.id
            if connection_obj.active and connection_obj.state == 'enable' and getattr(connection_obj, 'connector_sale_order_%s' % (opr)):
                ctx = dict(self._context or {})
                ctx['instance_id'] = instance_id
                if 'itemData' in ctx:
                    ctx['itemData']['send_email'] = connection_obj.notify
                connection = self.env[
                    'connector.instance'].with_context(ctx)._create_connection()
                if hasattr(self, '%s_after_order_%s' % (ecomm, opr)):
                    response = getattr(self, '%s_after_order_%s' % (ecomm, opr))(connection, increment_id, ecomm_order_id)
                self._cr.commit()
            else :
                response.update({
                    'status': 'no',
                    'text': '{0} {1} Error For Order {2} >> {0} instance is not connected.'.format(ecomm.capitalize(), opr, increment_id),
                })
            self.env['connector.sync.history'].create({
                'status': response.get('status', 'no'),
                'action_on': 'order',
                'action': 'b',
                'instance_id':instance_id,
                'error_message': response.get('text', 'no')
            })
        return response
