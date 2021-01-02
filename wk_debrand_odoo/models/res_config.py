# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
import base64, os
from odoo import fields, models, api, tools
import logging
_logger = logging.getLogger(__name__)

class IrDefault(models.Model):
    _inherit = 'ir.default'

    @api.model
    def set_wk_favicon(self, model, field):
        script_dir = os.path.dirname(__file__)
        rel_path = "../static/src/img/favicon.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            self.set('res.config.settings', 'wk_favicon', encoded_string.decode("utf-8"))

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wk_favicon = fields.Binary(string="Favicon Image")
    title_brand = fields.Char(string="Title Brand")
    odoo_text_replacement = fields.Char(string='Replace Text "Odoo" With?')
    favicon_url = fields.Char(string="Url")

    @api.model
    def get_debranding_settings(self):
        IrDefault = self.env['ir.default'].sudo()
        wk_favicon = IrDefault.get('res.config.settings', "wk_favicon")
        title_brand = IrDefault.get('res.config.settings', "title_brand")
        odoo_text_replacement = IrDefault.get('res.config.settings', "odoo_text_replacement")
        favicon_url = IrDefault.get('res.config.settings', "favicon_url")
        return {
            'wk_favicon': wk_favicon,
            'title_brand': title_brand,
            'odoo_text_replacement': odoo_text_replacement,
            'favicon_url': favicon_url,
        }

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', "wk_favicon", self.wk_favicon.decode("utf-8"))
        IrDefault.set('res.config.settings', "title_brand", self.title_brand)
        IrDefault.set('res.config.settings', "odoo_text_replacement", self.odoo_text_replacement)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = base_url+'/web/image/?model=res.config.settings&id='+str(self.id)+'&field=wk_favicon'
        IrDefault.set('res.config.settings', "favicon_url", image_url)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        wk_favicon = IrDefault.get('res.config.settings', "wk_favicon")
        title_brand = IrDefault.get('res.config.settings', "title_brand")
        odoo_text_replacement = IrDefault.get('res.config.settings', "odoo_text_replacement")
        favicon_url = IrDefault.get('res.config.settings', 'favicon_url')
        res.update(
            wk_favicon = wk_favicon,
            title_brand = title_brand,
            odoo_text_replacement = odoo_text_replacement,
            favicon_url = favicon_url,
        )
        return res