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
  "name"                 :  "Product Images In Order Lines",
  "summary"              :  """View product images in list view/order line.""",
  "category"             :  "Webkul Software Pvt. Ltd.",
  "version"              :  "2.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Product-Images-In-Order-Lines.html",
  "description"          :  """http://webkul.com/blog/product-images-order-line/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_list_view_image&version=12.0",
  "depends"              :  [
                             'sale',
                             'purchase',
                             'stock',
                            ],
  "data"                 :  [
                             'views/wk_list_view_image_assets.xml',
                             'views/product_view.xml',
                             'views/sale_view.xml',
                             'views/purchase_view.xml',
                             'views/stock_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  25,
  "currency"             :  "EUR",
}