odoo.define('order_list_refresh.refresh_order', function (require) {
    'use strict';

    var ListController = require('web.ListController');
    var ControlPanelController = require('web.ControlPanelController');
    var stop = false;

    ListController.include({
        init: function (parent, state, params) {
            var self = this;
            stop = false;
            setTimeout(function() {
                self.check_for_refresh(parent, params);
            }, 30000);
            return this._super.apply(this, arguments);;
        },
        check_for_refresh: function(parent, params) {
            var self = this;
            var obj = parent.actions;
            var data = obj[Object.keys(obj)[0]];
            if (data.res_model === 'sale.order' && (!stop)) {
                self.do_action(data.xml_id, {
                    clear_breadcrumbs: true
                });
            }
        },
    });

    ControlPanelController.include({
        init: function (parent, state, params) {
            stop = true;
            return this._super.apply(this, arguments);
        },
    });
});
