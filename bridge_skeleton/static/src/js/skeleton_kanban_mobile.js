odoo.define('bridge_skeleton.SkeletonKanbanMobile', function (require) {
    "use strict";
    
    var config = require('web.config');
    var SkeletonKanbanWidget = require('bridge_skeleton.SkeletonKanbanWidget');
    var SkeletonKanbanController = require('bridge_skeleton.SkeletonKanbanController');
    
    if (!config.device.isMobile) {
        return;
    }
    
    SkeletonKanbanWidget.include({
        template: "SkeletonKanbanWidgetMobile",
        init: function (parent, params) {
            this._super.apply(this, arguments);
            this.keepOpen = params.keepOpen || undefined;
        },
    });
    
    SkeletonKanbanController.include({
        init: function () {
            this._super.apply(this, arguments);
            this.openWidget = false;
        },
        _renderSkeletonKanbanWidget: function () {
            this.widgetData.keepOpen = this.openWidget;
            this.openWidget = false;
            return this._super.apply(this, arguments);
        },
    
      
    });
    
    });
    