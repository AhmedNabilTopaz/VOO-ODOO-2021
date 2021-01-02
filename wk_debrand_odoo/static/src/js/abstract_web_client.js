/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_debrand_odoo.web_client', function (require) {
"use strict";
    var WebClient = require('web.WebClient');
    var core = require('web.core');
    var config = require('web.config');
    var session = require('web.session');
    var utils = require('web.utils');
    var _t = core._t;





    WebClient.include({
        init: function(parent) {
            this._super.apply(this, arguments);
            var self = this;
            self._rpc({
                model: "res.config.settings",
                method: 'get_debranding_settings',
            }, {
                shadow: true
            }).then(function(debranding_settings){
                odoo.debranding_settings = debranding_settings;
                self.set('title_part', {"zopenerp": odoo.title_brand && odoo.title_brand.trim() || ''});
            });
        },
        start: function () {
            var self = this;
    
            // we add the o_touch_device css class to allow CSS to target touch
            // devices.  This is only for styling purpose, if you need javascript
            // specific behaviour for touch device, just use the config object
            // exported by web.config
            this.$el.toggleClass('o_touch_device', config.device.touch);
            this.on("change:title_part", this, this._title_changed);
            this._title_changed();
    
            var state = $.bbq.getState();
            // If not set on the url, retrieve cids from the local storage
            // of from the default company on the user
            var current_company_id = session.user_companies.current_company[0]
            if (!state.cids) {
                state.cids = utils.get_cookie('cids') !== null ? utils.get_cookie('cids') : String(current_company_id);
            }
            var stateCompanyIDS = _.map(state.cids.split(','), function (cid) { return parseInt(cid) });
            var userCompanyIDS = _.map(session.user_companies.allowed_companies, function(company) {return company[0]});
            // Check that the user has access to all the companies
            if (!_.isEmpty(_.difference(stateCompanyIDS, userCompanyIDS))) {
                state.cids = String(current_company_id);
                stateCompanyIDS = [current_company_id]
            }
            // Update the user context with this configuration
            session.user_context.allowed_company_ids = stateCompanyIDS;
            $.bbq.pushState(state);
            // Update favicon
            self._rpc({
                model: "res.config.settings",
                method: 'get_debranding_settings',
            }, {
                shadow: true
            }).then(function(debranding_settings){
                odoo.debranding_settings = debranding_settings;
                $("link[type='image/x-icon']").attr('href', odoo.debranding_settings.favicon_url)

            });


    
            return session.is_bound
                .then(function () {
                    self.$el.toggleClass('o_rtl', _t.database.parameters.direction === "rtl");
                    self.bind_events();
                    return Promise.all([
                        self.set_action_manager(),
                        self.set_loading()
                    ]);
                }).then(function () {
                    if (session.session_is_valid()) {
                        return self.show_application();
                    } else {
                        // database manager needs the webclient to keep going even
                        // though it has no valid session
                        return Promise.resolve();
                    }
                }).then(function () {
                    // Listen to 'scroll' event and propagate it on main bus
                    self.action_manager.$el.on('scroll', core.bus.trigger.bind(core.bus, 'scroll'));
                    core.bus.trigger('web_client_ready');
                    odoo.isReady = true;
                    if (session.uid === 1) {
                        self.$el.addClass('o_is_superuser');
                    }
                });
        },
    });


});