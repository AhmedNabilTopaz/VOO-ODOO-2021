# -*- coding: utf-8 -*-
#################################################################################
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
#################################################################################
{
  "name"                 :  "Odoo Delivery Boy",
  "summary"              :  """This module allows you to assign delivery boys and manage delivery of orders through native mobile application.""",
  "version"              :  "1.1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Anuj Kumar Chhetri",
  "website"              :  "",
  "description"          :  """Delivery Boy""",
  "live_test_url"        :  "http://demo.webkul.com/web/login",
  "depends"              :  [
                             'stock',
                             'website_sale',
                            ],
  "data"                 :  [
                             'security/delivery_boy_access.xml',
                             'security/ir.model.access.csv',
                             'views/delivery_token_email.xml',
                             'data/default_delivery_boy_data.xml',
                             'data/delivery_boy_sequence_data.xml',
                             'wizard/select_delivery_boy_wizard_view.xml',
                             'wizard/msg_wizard_view.xml',
                             'views/res_partner_view.xml',
                             'views/res_users_view.xml',
                             'views/delivery_boy_view.xml',
                             'views/stock_picking_view.xml',
                             'views/delivery_boy_pickings_view.xml',
                             'views/res_config_settings_view.xml',
                             'views/delivery_boy_programs_view.xml',
                             'views/account_invoice_view.xml',
                             'views/delivery_boy_config_view.xml',
                            ],
  "demo"                 :  ['data/delivery_boy_demo.xml'],
  "images"               :  ['static/description/Delivery-boy-App-Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  299,
  "currency"             :  "EUR",
}
