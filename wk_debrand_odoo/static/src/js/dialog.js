/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_debrand_odoo.dialog', function (require) {
"use strict";
    var Dialog = require('web.Dialog');
    
    Dialog.include({
        init: function (parent, options) {
            var self = this;
            var options = options || {};
            var odoo_text_replacement = '';
            if(odoo.debranding_settings && odoo.debranding_settings.odoo_text_replacement) 
                odoo_text_replacement = odoo.debranding_settings.odoo_text_replacement.trim();
            if (options.title && typeof(options.title) =='string'){
                var title = options.title.replace(/odoo/gi,odoo_text_replacement);
                options.title = title;
            } else
                options.title = odoo_text_replacement;
           
            if (options.$content){
                var $content = $(options.$content)
                var content_text = $content.html();
                content_text = content_text.replace(/odoo/gi,odoo_text_replacement);
                $content.html(content_text);
            }
            self._super(parent, options);
        },
    });
});