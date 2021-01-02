/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_debrand_odoo.web_settings_dashboard', function (require) {
    "use strict";
    var dashboad = require("web_settings_dashboard");

    dashboad.DashboardShare.include({
        init: function(parent, data){
            this._super(parent, data);
            this.share_url = '';
            this.share_text = encodeURIComponent("");
        },
        share_twitter: function(){
            var popup_url = _.str.sprintf( 'https://twitter.com/');
            this.sharer(popup_url);
        },
        share_facebook: function(){
            var popup_url = _.str.sprintf('https://www.facebook.com/');
            this.sharer(popup_url);
        },
        share_linkedin: function(){
            var popup_url = _.str.sprintf('http://www.linkedin.com/');
            this.sharer(popup_url);
        },
    });
});