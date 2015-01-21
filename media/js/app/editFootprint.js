(function() {

    EditFootprintView = Backbone.View.extend({
        initialize: function(options) {
            _.bindAll(this, 'render');

            // Modifying X-Editable default properties
            jQuery.fn.editable.defaults.mode = 'inline';

            jQuery.fn.editable.defaults.ajaxOptions = {
               headers: {'X-HTTP-Method-Override': 'PATCH'}
            };

            jQuery('.editable').editable({
                namedParams: true
            });

            jQuery('.editable-actor').editable({
                namedParams: true,
                template: '#editable-actor-form',
                validate: function(value) {
                    if (value.indexOf('name=&role') === 0) {
                        return 'Please enter the person\'s name'; 
                    }
                }
            });

            jQuery('.editable-language').editable({
                namedParams: true,
                source: options.languages,
                select2: {
                    multiple: true,
                    width: 200,
                    placeholder: 'Select language(s)',
                    allowClear: true
                }
            });

            jQuery('.do-you-know').on('save', function(e, params) {
                var dataName = jQuery(e.currentTarget).data('name');
                var elts = jQuery('[data-name="' + dataName + '"]').not(e.currentTarget);
                jQuery(elts).each(function(index) {
                    if (jQuery(this).is('.editable, .editable-language')) {
                        jQuery(this).editable('setValue', params.newValue, true);
                    }
                    jQuery(this).parents('div.description-list').show();
                });
                jQuery(e.currentTarget).parents('li').fadeOut(function() {
                    jQuery(this).remove();
                });
            });
        }
    });
})();