(function() {
    window.ObjectWorkspace = {
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

    ObjectWorkspace.Views.DetailView = Backbone.View.extend({
        events: {
            'click .inline-value': 'onClickField'
        },
        initialize: function(options) {
            _.bindAll(this, 'onClickField');
        },
        onClickField: function(event) {
            event.preventDefault();
            jQuery(event.currentTarget).toggle();
            jQuery(event.currentTarget).next().toggle();
            return false;
        },
    });
    
    var detailView = new ObjectWorkspace.Views.DetailView({
        el: jQuery("div.object-detail")
    });
    
    ObjectWorkspace.initialize();
    Backbone.history.start();
})();