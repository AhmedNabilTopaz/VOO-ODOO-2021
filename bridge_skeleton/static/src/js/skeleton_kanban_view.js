odoo.define('bridge_skeleton.SkeletonKanbanView', function (require) {
"use strict";

var SkeletonKanbanController = require('bridge_skeleton.SkeletonKanbanController');
var SkeletonKanbanModel = require('bridge_skeleton.SkeletonKanbanModel');
var SkeletonKanbanRenderer = require('bridge_skeleton.SkeletonKanbanRenderer');

var core = require('web.core');
var KanbanView = require('web.KanbanView');
var view_registry = require('web.view_registry');

var _lt = core._lt;

var skeletonKanbanView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Controller: SkeletonKanbanController,
        Model: SkeletonKanbanModel,
        Renderer: SkeletonKanbanRenderer,
    }),
    display_name: _lt('skeleton Kanban'),
});

view_registry.add('skeleton_kanban', skeletonKanbanView);

return skeletonKanbanView;

});
