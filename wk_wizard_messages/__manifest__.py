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
  "name"                 :  "Webkul Message Wizard",
  "summary"              :  """To show messages/warnings in Odoo""",
  "category"             :  "Tools",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  """""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_wizard_messages&version=12.0",
  "data"                 :  ['wizard/wizard_message_view.xml'],
  "images"               :  ['static/description/Banner.png'],
  "installable"          :  True,
  "pre_init_hook"        :  "pre_init_check",
}