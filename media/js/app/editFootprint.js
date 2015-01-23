(function() {

    EditFootprintView = Backbone.View.extend({
        events: {
            'click a.remove-footprint-actor span.glyphicon-remove': 'onConfirmRemoveActor',
            'click .btn-confirm': 'removeActor'
        },
        initialize: function(options) {
            _.bindAll(this, 'render', 'onConfirmRemoveActor', 'removeActor');
            
            var html = jQuery("#actor-display-template").html();
            this.actor_template = _.template(html);
                
            var self = this;

            // Modifying X-Editable default properties
            jQuery.fn.editable.defaults.mode = 'inline';
            jQuery.fn.editable.defaults.ajaxOptions = {
               headers: {'X-HTTP-Method-Override': 'PATCH'}
            };

            // Initializing X-editable fields
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
                },
                success: function(response, newValue) {
                    var html = self.actor_template(response);
                    jQuery('div.actor-list').append(html);
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
        },
        onConfirmRemoveActor: function(evt) {
            var anchor = jQuery(evt.currentTarget).parents('a')[0];
            var name = jQuery(anchor).data('name');
            var msg = "Are you sure you want to remove " + name + "?";
            
            jQuery("#confirm-modal").find('.modal-body').html(msg);
            var eltConfirm = jQuery("#confirm-modal").find('.btn-confirm')[0]; 
            jQuery(eltConfirm).data('params', jQuery(anchor).data('params'));
            jQuery(eltConfirm).data('url', jQuery(anchor).data('url'));
            
            jQuery("#confirm-modal").modal({
                'show': true,
                'backdrop': 'static',
                'keyboard': false
            });
        },
        removeActor: function(evt) {
            jQuery.ajax({
                url:,
                success: {
                   
               } 
            });
            alert('remove actor');
        }
    });
})();