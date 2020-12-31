odoo.define('bridge_skeleton.SkeletonKanbanRenderer', function (require) {
"use strict";


var skeletonKanbanRecord = require('bridge_skeleton.SkeletonKanbanRecord');

var KanbanRenderer = require('web.KanbanRenderer');

var skeletonKanbanRenderer = KanbanRenderer.extend({
    config: _.extend({}, KanbanRenderer.prototype.config, {
        KanbanRecord: skeletonKanbanRecord,
    }),
    start: function () {
        this.$el.addClass('o_skeleton_kanban_view position-relative align-content-start flex-grow-1 flex-shrink-1');
        return this._super.apply(this, arguments);
    },
});

return skeletonKanbanRenderer;

});
