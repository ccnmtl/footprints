(function() {
    
    DynamicModelForm = Backbone.Model.extend({
        urlRoot: '/record/form/',
        url: function() {
            return this.urlRoot + '?model=' + this.get('modelName');
        },
        fetch: function() {
            var self = this;
            jQuery.ajax({
                type: "GET",
                url: this.url(),
                dataType: 'json',
                success: function(json, textStatus, xhr) {
                    self.set({'state': json.state, 'formHtml': json.html});
                }
            });
        },
        update: function(frm) {
            var self = this;
            jQuery.ajax({
                type: "POST",
                url: frm.action,
                data: jQuery(frm).serializeArray(),
                dataType: 'json',
                success: function(json, textStatus, xhr) {
                    self.set({'state': json.state, 'formHtml': json.html});
                }
            });
        }
    });
    
    window.RecordFormView = Backbone.View.extend({
        events: {
            "click button[name='save']": 'onUpdate',
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onUpdate');
            this.parent = options.parent;
            this.model = new DynamicModelForm();
            this.model.on("change:formHtml", this.render);
            this.showForm = false;
        },
        setModel: function(modelName, showForm) {
            this.showForm = showForm;
            this.model.set('modelName', modelName);
            this.model.fetch();
        },
        onUpdate: function(evt) {
            evt.preventDefault();
            this.showForm = true;
            this.model.update(jQuery(evt.currentTarget).parents('form')[0]);
            return false;
        },
        render: function() {
            var state = this.model.get('state');

            if (state === 'saved') {
                this.parent.trigger('model.create');
            } else if (state === 'saving') {
                jQuery(this.el).html(this.model.get('formHtml'));
            } else if (state === 'view') {
                jQuery(this.el).html(this.model.get('formHtml'));
            }
            
            if (this.showForm) {
                jQuery(this.el).find('.dynamic-form-container').show();
            } else {
                jQuery(this.el).find('.dynamic-form-container').hide();
            }
            this.showForm = false;
        }
    });
    
    DynamicModelList = Backbone.Model.extend({
        urlRoot: '/record/list/',
        url: function() {
            return this.urlRoot +
                    '?model=' + this.get('modelName') +
                    '&offset=' + this.get('offset') ;
        },
        fetch: function() {
            var self = this;
            jQuery.ajax({
                type: "GET",
                url: this.url(),
                success: function(response) {
                    self.set('listHtml', response);
                }
            });
        }
    });
    
    window.RecordListView = Backbone.View.extend({
        initialize: function(options) {
            _.bindAll(this, 'render');
            this.list = new DynamicModelList();
            this.list.set('offset', 0);
            this.list.on("change:listHtml", this.render);
        },
        refresh: function() {
            this.list.fetch();
        },
        setModel: function(modelName) {
            this.list.set('modelName', modelName);
            this.list.fetch();
        },
        render: function() {
            jQuery(this.el).html(this.list.get('listHtml'));
        }
    });
    
    window.RecordWorkspaceView = Backbone.View.extend({
        events: {
            'click .list-group-item': 'onClickModelList',
            'click a.create': 'onShowCreateForm',
            'click a.disabled': 'onClickDisabledElement',
        },
        initialize: function(options) {
            _.bindAll(this, 'onClickModelList', 'onShowCreateForm', 'onCreated');
            this.formView = new RecordFormView({
                el: jQuery('div.model-form'), parent: this});
            this.listView = new RecordListView({el: jQuery('div.model-list')});
            
            this.on('model.create', this.onCreated, this);
        },
        onClickDisabledElement: function(evt) {
            evt.preventDefault();
            return false;
        },
        onClickModelList: function(evt) {
            var self = this;
            evt.preventDefault();
            
            jQuery('.list-group-item').removeClass('active');
            jQuery(evt.currentTarget).addClass('active');

            this.modelName = evt.currentTarget.hash.split("#")[1];
            this.formView.setModel(this.modelName, false);
            this.listView.setModel(this.modelName);
            return false;
        },
        onShowCreateForm: function(evt) {
            evt.preventDefault();
            this.formView.setModel(this.modelName, true);
            jQuery(this.listView.el).hide('fast');
            return false;
        },
        onCreated: function(evt) {
            this.listView.refresh();
            jQuery(this.listView.el).show('fast');
            jQuery(this.el).find('.dynamic-form-container').hide('fast');
        }
    });
})();