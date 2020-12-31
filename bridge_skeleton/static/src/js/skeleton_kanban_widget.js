odoo.define('bridge_skeleton.SkeletonKanbanWidget', function (require) {
    "use strict";
    
    var core = require('web.core');
    var relationalFields = require('web.relational_fields');
    var session = require('web.session');
    var Widget = require('web.Widget');
    
    var _t = core._t;
    var FieldMany2One = relationalFields.FieldMany2One;
    var FieldSelection = relationalFields.FieldSelection;
    
    var SkeletonSelection = FieldSelection.extend({
        start: function()
            {
                this.$el.addClass('w-100');
                return this._super.apply(this, arguments);
        },
        });
    
    var SkeletonMany2One = FieldMany2One.extend({
        
        start: function () {
            this.$el.addClass('w-100');
            return this._super.apply(this, arguments);
        }
    });
    
    var SkeletonKnabanWidget = Widget.extend({
        template: 'SkeletonKanbanWidget',
        custom_events: {
            field_changed: '_onInstanceChanged',
        },
    
        init: function (parent, params) {
            this._super.apply(this, arguments);
            this.connector_instace = params.instance_detail[1] || '';
            this.current_ecom = params.current_ecomm || [(0)];
            this.active = params.active || 'new';
            this.extensions = params.extensions;
            this.status = params.status || 'not_connected';
            this.bridge_name = params.bridge_name || 'Ecommerce';
            this.user_guide = params.user_guide || 'https://store.webkul.com/Magento-OpenERP-Bridge.html#tabreviews';
            this.rate_review = params.rate_review || 'https://webkul.com/blog/magento-openerp-bridge/';
            this.extension = params.extension || 'https://store.webkul.com/Magento-Extensions/ERP.html';
            this.SkeletonChannelField = this._createSelectionField('ecommerce_channels','connector.instance',this.current_ecom, this.extensions);
            this.bridge_short_form = params.bridge_short_form || 'Bridge';
            this.img_link = params.img_link || '/bridge_skeleton/static/src/img/magento-logo.png';
        },
        willStart: function () {
            var self = this;
            var superDef = this._super.apply(this, arguments);
    
            self.SkeletonInstanceField = self._createMany2One('instances', 'connector.instance', self.connector_instace, function () {
                        return [['ecomm_type', '=', self.current_ecom[0][0]]];
                    });
            return Promise.all([superDef]);
        },

        renderElement: function () {
            this._super.apply(this, arguments);
            this.SkeletonChannelField.appendTo(this.$('.o_skeleton_selecton_ecom'));
            this.SkeletonInstanceField.appendTo(this.$('.o_skeleton_instance_field'));
        },

        _createSelectionField: function(name, model, values, extensions , domain, context)
        {   
            var fields = {};
            fields[name] = {type: 'selection', relation: model,string : name , selection:extensions};
            var data = {};
            data[name] =values[0][0];
            var record = {
                id: name,
                fields: fields,
                model: 'dummy',
                fieldsInfo: {
                    default: fields,
                },
                data:data,
                getDomain: domain || function () { return []; },
                getContext: context || function () { return {}; },
            };
            var options = {
                mode: 'edit',
                noOpen: true,
                attrs: {
                    can_create: false,
                    can_write: false,
                }
            };
        return new SkeletonSelection(this, name, record, options);
        },
    
        _createMany2One: function (name, model, value,domain, context) {
            var fields = {};

            fields[name] = {type: 'many2one', relation: model, string: name};
            var data = {};
            data[name] = {data: {display_name: value}};
            var record = {
                id: name,
                res_id: 1,
                model: 'dummy',
                fields: fields,
                fieldsInfo: {
                    default: fields,
                },
                data: data,
                getDomain: domain || function () { return []; },
                getContext: context || function () { return {}; },
            };
            var options = {
                mode: 'edit',
                noOpen: true,
                attrs: {
                    can_create: false,
                    can_write: false,
                }
            };
            return new SkeletonMany2One(this, name, record, options);
        },
        
    
        _onInstanceChanged: function (ev) {
            console.log(ev.data.dataPointID);
            ev.stopPropagation();
            if (ev.data.dataPointID === 'ecommerce_channels') {
                this.trigger_up('change_channel', {channel_id: ev.data.changes.ecommerce_channels});
            }
            
            
            if (ev.data.dataPointID === 'instances') {
                this.trigger_up('change_instance', {instance_id: ev.data.changes.instances.id});
            }
           
           
        },
       
    });
    
    return SkeletonKnabanWidget;
    
    });
    