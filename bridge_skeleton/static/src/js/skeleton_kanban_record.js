odoo.define('bridge_skeleton.SkeletonKanbanRecord', function (require) {
    "use strict";

    var KanbanRecord = require('web.KanbanRecord');

    var SkeletonKanbanRecord = KanbanRecord.extend({
        events: _.extend({}, KanbanRecord.prototype.events, {
            'click': '_onSelectRecord',
        }),

        _onSelectRecord: function (ev) {
            ev.preventDefault();
            if (!$(ev.target).hasClass('oe_kanban_action')) {
                this.trigger_up('open_wizard', {productId: this.recordData.product_id});
            }
        },
    });

    return SkeletonKanbanRecord;

    });
