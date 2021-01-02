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
  "name"                 :  "Odoo Keep initial address for orders",
  "summary"              :  """Odoo Keep initial address for orders""",
  "category"             :  "website",
  "version"              :  "1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Keep-Initial-Address-For-Orders.html",
  "description"          :  """This module works very well with latest version of Odoo 13.0
--------------------------------------------------------------""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=order_initial_address",
  "depends"              :  [
                             'sale_management',
                             'wk_wizard_messages',
                            ],
  "data"                 :  [
                             'views/sale_views.xml',
                             'views/account_invoice_view.xml',
                             'data/address_server_actions.xml',
                             'report/sale_portal_templates.xml',
                             'report/report_invoice.xml',
                             'report/sale_report_templates.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  35,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}