# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################

from odoo import api, models
from odoo import SUPERUSER_ID
from odoo.http import request

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    rerouting_limit = 10
    _geoip_resolver = None

    @classmethod
    def binary_content(cls, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None,filename_field='datas_fname', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None,related_id=None, access_mode=None,env=None):
        env = env or request.env
        obj = None
        if xmlid:
            obj = env.ref(xmlid, False)
        elif id and model in env:
            obj = env[model].browse(int(id))
        if obj._name == "res.partner" and field in ("image"):
            env = env(user=SUPERUSER_ID)
        return super(Http, cls).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype=default_mimetype,access_token=access_token,related_id=related_id, access_mode=access_mode, env=env)
