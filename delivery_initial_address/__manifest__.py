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
  "name"                 :  "Odoo Keep initial address for delivery",
  "summary"              :  """Odoo Keep initial address for delivery""",
  "category"             :  "sales",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo-Keep-Initial-Address-For-Delivery.html",
  "description"          :  """Keep initial address in picking""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=delivery_initial_address&version=13.0",
  "depends"              :  [
                             'wk_wizard_messages',
                             'stock',
                            ],
  "data"                 :  [
                             'views/stock_picking_views.xml',
                             'data/address_server_actions.xml',
                             'report/report_deliveryslip.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  25,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}