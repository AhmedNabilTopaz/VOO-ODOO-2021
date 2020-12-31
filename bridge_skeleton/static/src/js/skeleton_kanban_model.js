odoo.define('bridge_skeleton.SkeletonKanbanModel', function (require) {
    "use strict";
    
    
    
    var KanbanModel = require('web.KanbanModel');
    
    var SkeletonKanbanModel = KanbanModel.extend({
        
        init: function () {
            this.instance_id = false;
            this.channel_id = false;
            this._super.apply(this, arguments);
            
        },
        load: function () {
            var self = this;
            var args = arguments;
            var _super = this._super;
       
            return this._getInstanceId().then(function (instance_id) {
                var params = args[0];
                self.instance_id = instance_id;
                self._addOrUpdate(params.domain, ['instance_id', 'in', [instance_id]]);
    
                return _super.apply(self, args);
            });
        },
        reload: function (id, options) {
            var domain = options && options.domain || this.localData[id].domain;
    
            this._addOrUpdate(domain,['instance_id', '=',this.instance_id]);
            options = _.extend(options, {domain: domain});
    
            return this._super.apply(this, arguments);
        },
        _getInstanceId: function () {
            return this._rpc({
                route: '/bridge_skeleton/get_instance_id'
            });
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        _addOrUpdate: function (domain, subDomain) {
            var key = subDomain[0];
            var index = _.findIndex(domain, function (val) {
                return val[0] === key;
            });
    
            if (index < 0) {
                domain.push(subDomain);
            } else {
                domain[index] = subDomain;
            }
    
            return domain;
        },
        _updateInstance: function (instance_id) {
            this.instance_id = instance_id;
            return Promise.resolve();
        },
        _updateChannel: function (instance_id) {
            this.instance_id = instance_id;
            return Promise.resolve();
        },
    
    });
    
    return SkeletonKanbanModel;
    
    });
    