
from odoo import exceptions, api, models, fields
from datetime import date
import logging

_logger = logging.getLogger('__product_sync__')


class ConnectorProductImage(models.Model):
    _inherit = ["product.image"]

    extra_image_ids = fields.One2many('connector.extra.image', 'image_id')
    position = fields.Integer(string='Position')
