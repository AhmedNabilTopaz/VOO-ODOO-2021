# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from . import models


def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    versionInfo = common.exp_version()
    serverSerie = versionInfo.get('server_serie')
    if serverSerie != '13.0':
        raise Warning(
            'Module support Odoo series 13.0 found {}.'.format(serverSerie))
