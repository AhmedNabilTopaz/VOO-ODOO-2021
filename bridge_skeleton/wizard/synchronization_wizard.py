# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models


class SynchronizationWizard(models.TransientModel):
    _name = 'synchronization.wizard'
    _description = "Synchronization Wizard"

    def _default_instance_name(self):
        return self.env['connector.instance'].search([], limit=1).id

    action = fields.Selection([('export', 'Export'), ('update', 'Update')], string='Action', default="export", required=True,
                              help="""Export: Export all Odoo Category/Products at other E-commerce. Update: Update all synced products/categories at other E-commerce, which requires to be update at other E-commerce""")
    instance_id = fields.Many2one('connector.instance', string='Ecommerce Instance', default=lambda self: self._default_instance_name())

    def start_attribute_synchronization(self):
        ctx = dict(self._context or {})
        ctx['instance_id'] = self.instance_id.id
        ctx['ecomm_channel'] = self.instance_id.ecomm_type
        message = self.env['connector.snippet'].with_context(
            ctx).export_attributes_and_their_values()
        return message

    def start_category_synchronization(self):
        ctx = dict(self._context or {})
        ctx['sync_opr'] = self.action
        ctx['instance_id'] = self.instance_id.id
        ctx['ecomm_channel'] = self.instance_id.ecomm_type
        message = self.env['connector.snippet'].with_context(
            ctx).sync_operations('product.category', 'connector.category.mapping', [], 'category')
        return message

    def start_category_synchronization_mapping(self):
        ctx = dict(self._context or {})
        mapped_ids = ctx.get('active_ids')
        map_objs = self.env['connector.category.mapping'].browse(mapped_ids)
        map_categ_ids = map_objs.mapped('name').ids
        ctx.update(
            sync_opr=self.action,
            instance_id=self.instance_id.id,
            ecomm_channel=self.instance_id.ecomm_type,
            active_model='product.category',
            active_ids=map_categ_ids,
        )
        message = self.env['connector.snippet'].with_context(
            ctx).sync_operations('product.category', 'connector.category.mapping', [], 'category')
        return message

    def start_bulk_category_synchronization_mapping(self):
        partial = self.create({'action': 'update'})
        ctx = dict(self._context or {})
        ctx['mapping_categ'] = False
        return {'name': "Synchronization Bulk Category",
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'synchronization.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    def start_product_synchronization(self):
        ctx = dict(self._context or {})
        ctx['sync_opr'] = self.action
        ctx['instance_id'] = self.instance_id.id
        ctx['ecomm_channel'] = self.instance_id.ecomm_type
        message = self.env['connector.snippet'].with_context(
            ctx).sync_operations('product.template', 'connector.template.mapping', [('type', '!=', 'service')], 'product')
        return message

    def start_product_synchronization_mapping(self):
        ctx = dict(self._context or {})
        mapped_ids = ctx.get('active_ids')
        map_objs = self.env['connector.template.mapping'].browse(mapped_ids)
        map_product_ids = map_objs.mapped('name').ids
        ctx.update(
            sync_opr=self.action,
            instance_id=self.instance_id.id,
            ecomm_channel=self.instance_id.ecomm_type,
            active_model='product.template',
            active_ids=map_product_ids,
        )
        message = self.env['connector.snippet'].with_context(
            ctx).sync_operations('product.template', 'connector.template.mapping', [('type', '!=', 'service')], 'product')
        return message

    def start_bulk_product_synchronization_mapping(self):
        partial = self.create({'action': 'update'})
        ctx = dict(self._context or {})
        ctx['mapping'] = False
        return {'name': "Synchronization Bulk Product",
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'synchronization.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    @api.model
    def start_bulk_product_synchronization(self):
        partial = self.create({})
        ctx = dict(self._context or {})
        ctx['check'] = False
        return {'name': "Synchronization Bulk Product",
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'synchronization.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    @api.model
    def start_bulk_category_synchronization(self):
        partial = self.create({})
        ctx = dict(self._context or {})
        ctx['All'] = True
        return {'name': "Synchronization Bulk Category",
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'synchronization.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    def reset_mapping(self):
        domain = [('instance_id', '=', self.instance_id.id)]
        channel = self.instance_id.ecomm_type
        models = ['connector.attribute.mapping', 'connector.category.mapping', 'connector.option.mapping','connector.order.mapping',
            'connector.partner.mapping', 'connector.product.mapping', 'connector.template.mapping', 'connector.sync.history']
        if hasattr(self, 'reset_%s_mapping' % channel):
            response = getattr(self, 'reset_%s_mapping' % channel)(domain)
            if response:
                models.extend(response or [])
        for model in models:
            self.unlink_tables(model, domain)
        return self.env['message.wizard'].genrated_message("<h4 class='text-success'><i class='fa fa-smile-o'></i> Mappings has been deleted successfully</h4>")

    def unlink_tables(self, model, domain=[]):
        record_objs = self.env[model].search(domain)
        if record_objs:
            record_objs.unlink()
