# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_confirm(self, *args, **kwargs):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        """
        res = super(StockMove, self)._action_confirm(*args, **kwargs)
        ctx = dict(self._context or {})
        ctx['stock_operation'] = '_action_confirm'
        res.with_context(ctx).fetch_stock_warehouse()
        return res

    def _action_cancel(self, *args, **kwargs):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        """
        ctx = dict(self._context or {})
        ctx['action_cancel'] = True
        ctx['stock_operation'] = '_action_cancel'

        check = False
        for obj in self:
            if obj.state == "cancel":
                check = True
        res = super(StockMove, self)._action_cancel(*args, **kwargs)
        if not check:
            self.with_context(ctx).fetch_stock_warehouse()
        return res

    def _action_done(self, *args, **kwargs):
        """ Process completly the moves given as ids and if all moves are done, it will finish the picking.
        """
        ctx = dict(self._context or {})
        ctx['stock_operation'] = '_action_done'
        res = super(StockMove, self)._action_done(*args, **kwargs)
        self.with_context(ctx).fetch_stock_warehouse()
        return res

    def fetch_stock_warehouse(self):
        ctx = dict(self._context or {})
        if 'stock_from' not in ctx:
            ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
            for data in self:
                odoo_product_id = data.product_id.id
                flag = 1
                if data.origin:
                    sale_objs = data.env['sale.order'].search(
                        [('name', '=', data.origin)])
                    if sale_objs:
                        order_channel = sale_objs[0].ecommerce_channel
                        if order_channel in ecomm_cannels and data.picking_id \
                                and data.picking_id.picking_type_code == 'outgoing':
                            flag = 0
                else:
                    flag = 2  # no origin
                warehouse_id = 0
                if flag == 1:
                    warehouse_id = data.warehouse_id.id
                if flag == 2:
                    location_obj = data.location_dest_id
                    company_id = data.company_id.id
                    warehouse_id = self.check_warehouse_location(
                        location_obj, company_id)  # Receiving Goods
                    if not warehouse_id:
                        location_obj = data.location_id
                        warehouse_id = self.check_warehouse_location(
                            location_obj, company_id)  # Sending Goods
                if warehouse_id:
                    data.check_warehouse(
                        odoo_product_id, warehouse_id, ecomm_cannels)
        return True

    @api.model
    def check_warehouse_location(self, location_obj, company_id):
        warehouse_model = self.env['stock.warehouse']
        while location_obj:
            warehouse_obj = warehouse_model.search([
                ('lot_stock_id', '=', location_obj.id),
                ('company_id', '=', company_id)
            ], limit=1)
            if warehouse_obj:
                return warehouse_obj.id
            location_obj = location_obj.location_id
        return False

    @api.model
    def check_warehouse(self, odoo_product_id, warehouse_id, ecomm_cannels):
        for ecomm in ecomm_cannels:
            if hasattr(self, '%s_stock_update' % ecomm):
                getattr(self, '%s_stock_update' % ecomm)(odoo_product_id, warehouse_id)

        return True