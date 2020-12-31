odoo.define('bridge_skeleton.SkeletonKanbanController', function (require) {
    "use strict";
    
  
    
    var core = require('web.core');
    var KanbanController = require('web.KanbanController');
    var SkeletonKanbanWidget = require('bridge_skeleton.SkeletonKanbanWidget');    
    var _t = core._t;
    
    var SkeletonKanbanController = KanbanController.extend({
        custom_events: _.extend({}, KanbanController.prototype.custom_events, {
            change_instance: '_onInstanceChanged',
            change_channel: '_onChannelChanged'

           
        }),

        init: function () {
            this.channel_id = null;
            this.instance_id = null;
            this.editMode = false;
            this.updated = false;
            this.widgetData = null;
            return this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this.$('.o_content').append($('<div>').addClass('o_skeleton_kanban'));
            return this._super.apply(this, arguments).then(function () {
                self.$('.o_skeleton_kanban').append(self.$('.o_kanban_view'));
            });
         

        },
    
    
        _fetchWidgetData: function () {
            var self = this;
    
            return this._rpc({
                route: '/bridge_skeleton/infos',
            }).then(function (data) {
                self.widgetData = data;
                return self.model._updateInstance(data.instance_detail[0]);
            });
        },
        _renderSkeletonKanbanWidget: function () {
          
                var self = this;
                var oldWidget = this.widget;
                this.widget = new SkeletonKanbanWidget(this, _.extend(this.widgetData, {edit: this.editMode}));
                return this.widget.appendTo(document.createDocumentFragment()).then(function () {
                    self.$('.o_skeleton_kanban').prepend(self.widget.$el);
                    if (oldWidget) {
                        oldWidget.destroy();
                    }
                });
           },

      
        _update: function () {
          
                var def = this._fetchWidgetData().then(this._renderSkeletonKanbanWidget.bind(this));
                return Promise.all([def, this._super.apply(this, arguments)]);
        },
        _onInstanceChanged: function (ev) {
            ev.stopPropagation();
            var self = this;
            this.instance_id = ev.data.instance_id;
            this._rpc({
                route: '/bridge_skeleton/skeleton_instance_set',
                params: {
                    instance_id: ev.data.instance_id,
                },
            }).then(function () {
                self.model._updateInstance(ev.data.instance_id).then(function () {
                    self.reload();
                });
            });
        },
        _onChannelChanged: function (ev) {
            ev.stopPropagation();
            var self = this;
            this.channel_id = ev.data.channel_id;
            this._rpc({
                route: '/bridge_skeleton/skeleton_channel_set',
                params: {
                    channel_id: ev.data.channel_id,
                },
            }).then(function (instance_id) {
                self.model._updateChannel(instance_id).then(function () {
                    self.reload();
                });
                
            });
        },
    });
    
    return SkeletonKanbanController;
    
    });
    