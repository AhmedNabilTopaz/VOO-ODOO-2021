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
  "name"                 :  "Odoo Backend Debranding",
  "summary"              :  "This is the base odoo backend debranding module.",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.3",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  "This is the base odoo backend debranding module.",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_debrand_odoo",
  "depends"              :  ['web','mail', 'portal'],
  "data"                 :  [
                              'views/res_config_view.xml',
                              'views/web_client_template.xml',
                              'views/portal_templates.xml',
                              'views/email_templates.xml',
                              'views/templates.xml',
                              'data/data.xml',
                            ],
  "qweb"                 :  [
                              'static/src/xml/base.xml',
                              'static/src/xml/client_action.xml',
                              'static/src/xml/dashboard.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  30,
  "currency"             :  "EUR",
}
