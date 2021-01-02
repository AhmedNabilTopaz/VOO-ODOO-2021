/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_debrand_odoo.bot', function (require) {
    "use strict";

    var Message = require('mail.model.Message');

    Message.include({
        _getAuthorName: function () {
            if (this._isOdoobotAuthor()) {
                return "System";
            }
            return this._super.apply(this, arguments);
        },
    });
});
