
from odoo import exceptions, api, models, fields
from datetime import date


class ConnectorExtraImage(models.Model):

    _name = "connector.extra.image"
    _description = "Connector Extra Image"
    
    _sql_constraints = [('unique_instace_extra_image', 'UNIQUE(image_id, instance_id)', 'Instances in Extra Images should be unique')]

    instance_id = fields.Many2one("connector.instance", "Connector Instance", required = True)
    ecommerce_channel = fields.Selection(string="eCommerce Channel", related ="instance_id.ecomm_type")
    image_id = fields.Many2one('product.image', "Extra Images")