# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('product_variant_ids', 'product_variant_ids.day_before_expiry')
    def _compute_day_before_expiry(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.day_before_expiry = template.product_variant_ids.day_before_expiry
        for template in (self - unique_variants):
            template.day_before_expiry = 0

    def _set_day_before_expiry(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.day_before_expiry = template.day_before_expiry

    @api.depends('product_variant_ids', 'product_variant_ids.alert_before_expiry')
    def _compute_alert_before_expiry(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.alert_before_expiry = template.product_variant_ids.alert_before_expiry
        for template in (self - unique_variants):
            template.alert_before_expiry = 0

    def _set_alert_before_expiry(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.alert_before_expiry = template.alert_before_expiry

    @api.depends('product_variant_ids', 'product_variant_ids.remove_before_expiry')
    def _compute_remove_before_expiry(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.remove_before_expiry = template.product_variant_ids.remove_before_expiry
        for template in (self - unique_variants):
            template.remove_before_expiry = 0

    def _set_remove_before_expiry(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.remove_before_expiry = template.remove_before_expiry

    day_before_expiry = fields.Integer(string='Number of days before expiry', compute='_compute_day_before_expiry', inverse='_set_day_before_expiry', store=True, help="Number of days before expiry")
    alert_before_expiry = fields.Integer(string='Alert days before expiry date', compute='_compute_alert_before_expiry', inverse='_set_alert_before_expiry', store=True, help="Alert days before expiry date")
    remove_before_expiry = fields.Integer(string='Removal days before expiry date', compute='_compute_remove_before_expiry', inverse='_set_remove_before_expiry', store=True, help="Removal days before expiry date")

class Product(models.Model):
    _inherit = "product.product"
    
    day_before_expiry = fields.Integer(string='Number of days before expiry', help="Number of days before expiry")
    alert_before_expiry = fields.Integer(string='Alert days before expiry date', help="Alert days before expiry date")
    remove_before_expiry = fields.Integer(string='Removal days before expiry date', help="Removal days before expiry date")
