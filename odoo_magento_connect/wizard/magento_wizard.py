# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################

from odoo import fields, models


class MagentoWizard(models.TransientModel):
    _name = "magento.wizard"
    _description = "Magento Wizard"

    magento_store_view = fields.Many2one(
        'magento.store.view', string='Default Magento Store')

    def button_select_default_magento_store(self):
        self.ensure_one()
        ctx = dict(self._context or {})
        if self._context.get('active_id'):
            self.env['connector.instance'].browse(self._context['active_id']).store_id = self.magento_store_view.id
        return self.env['message.wizard'].genrated_message(ctx.get('text', ''), name='Magento Connection Status')
