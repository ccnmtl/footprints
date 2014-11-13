(function() {
    
    DynamicModel = Backbone.Model.extend({
        view: function() {
            var self = this;
            self.set('formHtml', '');

            var url = '/record/view/?model=' + this.get('modelName');
            var pk = this.get('pk');
            if (pk !== undefined)
                url += '&pk=' + this.get('pk');

            jQuery.ajax({
                type: "GET",
                url: url,
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
                url: '/record/view/',
                data: jQuery(frm).serializeArray(),
                dataType: 'json',
                success: function(json, textStatus, xhr) {
                    self.set({'state': json.state, 'formHtml': json.html});
                }
            });
        },
        remove: function(frm) {
            var self = this;
            jQuery.ajax({
                type: "POST",
                url: '/record/delete/',
                data: jQuery(frm).serializeArray(),
                dataType: 'json',
                success: function(json, textStatus, xhr) {
                    self.set({'state': json.state, 'formHtml': json.html});
                }
            });
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
    
    window.RecordFormView = Backbone.View.extend({
        events: {
            "click button[name='save']": 'onSave',
            "click button[name='delete']": 'onDelete',
            "click button[name='confirm-delete']": 'onConfirmDelete'
        },
        initialize: function(options) {
            _.bindAll(this,  'onConfirmDelete', 'onDelete',  'onSave',
                'render', 'renderForm', 'showForm');
            
            var html = jQuery("#add-another-template").html();
            this.addTemplate = _.template(html);
            this.modal = options.modal;

            this.parent = options.parent;
            this.model = new DynamicModel();
            this.model.on("change:formHtml", this.render);
        },
        onConfirmDelete: function(evt) {
            jQuery("#confirm-modal").modal('hide');
            this.model.remove(jQuery(this.el).find('form')[0]);
            return true;
        },
        onDelete: function(evt) {
            evt.preventDefault();
            jQuery("#confirm-modal").modal({
                   'show': true,
                   'backdrop': 'static',
                   'keyboard': false
            });
            return false;
        },
        onSave: function(evt) {
            evt.preventDefault();
            this.model.update(jQuery(evt.currentTarget).parents('form')[0]);
            return false;
        },
        render: function() {
            var state = this.model.get('state');

            if (state === 'saved' || state === 'deleted') {
                this.hideForm();
                this.parent.trigger('model.saved');
            } else if (state === 'saving') {
                this.renderForm();
            } else if (state === 'view') {
                this.renderForm();
                this.showForm();
                this.parent.trigger('model.view');
            }        
        },
        renderForm: function() {
            var self = this;
            var elt = this.modal ? jQuery(this.el).find('.modal-body')[0] :
                    this.el;
            
            jQuery(elt).html(this.model.get('formHtml'));
            
            jQuery(elt).find('.add-another').each(function() {
                var html = self.addTemplate({});
                jQuery(this).after(html);
            });
            
            tinymce.init({selector:'textarea.wsywig'});
        },
        showForm: function() {
            if (this.modal) {
                this.the_modal = jQuery(this.el).modal({
                    'show': true,
                    'backdrop': 'static',
                    'keyboard': false
                });
            }
        },
        hideForm: function() {
            if (this.the_modal) {
                jQuery(this.the_modal).modal('hide');
            }
        }
    });
    
    window.RecordListView = Backbone.View.extend({
        initialize: function(options) {
            _.bindAll(this, 'render', 'refresh');
            this.parent = options.parent;
            this.list = new DynamicModelList();
            this.list.set('offset', 0);
            this.list.on("change:listHtml", this.render);
        },
        refresh: function() {
            this.list.fetch();
        },
        render: function() {
            jQuery(this.el).html(this.list.get('listHtml'));
            this.parent.trigger('model.list');
        }
    });
    
    window.RecordWorkspaceView = Backbone.View.extend({
        events: {
            'click a.disabled': 'onClickDisabledElement',
            'click .list-group-item': 'onSelectModel',
            'click a.create': 'onCreate',
            'click a.edit': 'onEdit',
            'click button[name="cancel"]': 'onCancel',
            "click a.add-another": 'onAddAnother'
        },
        initialize: function(options) {
            _.bindAll(this, 'onCancel', 'onCreate', 'onEdit',
                      'onSaved', 'onSelectModel', 'onView', 'onViewList',
                      'onAddAnother');

            this.formView = new RecordFormView({
                el: jQuery('div.model-form'), parent: this});
            this.listView = new RecordListView({
                el: jQuery('div.model-list'), parent: this});
            
            this.on('model.list', this.onViewList, this);
            this.on('model.view', this.onView, this);
            this.on('model.saved', this.onSaved, this);
        },
        onAddAnother: function(evt) {
            evt.preventDefault();
            this.popupFormView = new RecordFormView({
                el: jQuery("#foreign-key-model-form"),
                modal: true,
                parent: this
            });
            var modelName = jQuery(evt.currentTarget).prev('select').attr('name');
            this.popupFormView.model.set('modelName', modelName);
            this.popupFormView.model.view();
            return false;
        },
        onCancel: function(evt) {
            jQuery(this.formView.el).hide('fast');
            jQuery(this.listView.el).show('fast');
        },
        onClickDisabledElement: function(evt) {
            evt.preventDefault();
            return false;
        },
        onCreate: function(evt) {
            evt.preventDefault();
            this.formView.model.set('modelName', this.modelName);
            this.formView.model.set('pk', undefined);
            this.formView.model.view();
            return false;
        },
        onEdit: function(evt) {
            evt.preventDefault();
            var pk = jQuery(evt.currentTarget).data('pk');
            this.formView.model.set('modelName', this.modelName);
            this.formView.model.set('pk', pk);
            this.formView.model.view();
            return false;
        },
        onSaved: function() {
            if (this.popupFormView) {
                delete this.popupFormView;
                this.formView.model.view();
            } else {
                this.listView.refresh();
                jQuery(this.formView.el).hide('fast');
                jQuery(this.listView.el).show('fast');
            }
        },
        onSelectModel: function(evt) {
            var self = this;
            evt.preventDefault();
            
            var modelName = evt.currentTarget.hash.split("#")[1];
            if (this.modelName !== modelName) {
                // highlight selected model 
                jQuery('.list-group-item').removeClass('active');
                jQuery(evt.currentTarget).addClass('active');
    
                // save model name
                this.modelName = modelName;
                this.modelDisplayName = jQuery(evt.currentTarget).html();
                
                // fetch model list
                this.listView.list.set('modelName', this.modelName);
                this.listView.refresh();
            }
            return false;
        },        
        onView: function(evt) {
            jQuery(this.formView.el).show();
            jQuery(this.listView.el).hide();
        },
        onViewList: function(evt) {
            jQuery(this.el).find('.navbar .navbar-brand').html(this.modelDisplayName);
            jQuery(this.el).find('.navbar').show();
            jQuery(this.formView.el).hide();
            jQuery(this.listView.el).show();
        }
    });
})();