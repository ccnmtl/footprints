(function() {
    window.ObjectWorkspace = {
        Models: {},
        Views: {},

        initialize: function() {
                jQuery.fn.editable.defaults.mode = 'inline';
                jQuery.fn.editable.defaults.ajaxOptions = {
                   headers: {'X-HTTP-Method-Override': 'PATCH'}
                };
                jQuery('.editable').editable({namedParams: true});
                jQuery('.editable-language').editable({
                    namedParams: true,
                    source: [
                    {% for language in languages %}
                        {value: {{language.id}}, text: "{{language.name}}"}{% if not forloop.last %},{% endif %}
                    {% endfor %}]
                });
                jQuery('.editable').on('shown', function(e, editable) {
                    tinymce.init({selector: 'textarea'});
                });
            });
        }
    };
    
    ObjectWorkspace.Models.GenericObject = Backbone.Model.extend({
        urlRoot: ''
    });

    ObjectWorkspace.Views.DetailView = Backbone.View.extend({
        //events: {
        //    'click .inline-value': 'onClickField'
        //},
        initialize: function(options) {
            _.bindAll(this, 'render');

            this.template = _.template(jQuery(options.template).html());
            this.model = new GenericObject({'id': options.object_id});
            this.model.urlRoot = options.urlRoot;
            this.model.bind('change', this.render)
            this.model.fetch();
        },
        render: function() {
            // Only invoked once when the session model is instantiated
            this.el.innerHTML = this.template(this.session.toJSON());
        },
    });
    
    var detailView = new ObjectWorkspace.Views.DetailView({
        el: jQuery("div.object-detail")
    });
    
    ObjectWorkspace.initialize();
    Backbone.history.start();
})();