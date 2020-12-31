# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

{
    "name":" Bridge Extra Image",
    "version":"1.0.0.1",
    'category': 'Bridge Module',
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'https://store.webkul.com',
    'summary': 'Extra Category Image Module',
    'description': """
        Extra Category Image Module
    """,
    "depends":["base", "bridge_skeleton"],
    "data":[
        'security/ir.model.access.csv',
        "views/connector_extra_image_view.xml"
        # "views/connector_product_image_view.xml",
        # "views/connector_extra_image_template.xml"
        ],
    'installable': True,
}
